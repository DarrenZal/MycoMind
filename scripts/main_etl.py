"""
Main ETL Pipeline for MycoMind

This module orchestrates the complete Extract, Transform, Load process for
knowledge extraction. It coordinates configuration management, schema parsing,
LLM interactions, and Obsidian note generation to transform unstructured
input into structured knowledge graphs.

Future Enhancement: This module will be analyzed by the future build_project_kg.py
script to map the complete data flow and processing pipeline, demonstrating
how all system components work together in the project's knowledge graph.
"""

import os
import sys
import json
import logging
import argparse
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import hashlib
import pickle
from dataclasses import dataclass

# Import MycoMind modules
from config_manager import ConfigManager, load_config
from schema_parser import SchemaParser, SchemaDefinition
from obsidian_utils import ObsidianNoteGenerator, create_obsidian_generator

# LLM imports
import openai
try:
    import anthropic
except ImportError:
    anthropic = None

# Additional imports for file processing
import requests
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Results from processing a batch of data."""
    success: bool
    entities: List[Dict[str, Any]]
    errors: List[str]
    processing_time: float
    metadata: Dict[str, Any]


class LLMClient:
    """
    Unified client for different LLM providers.
    
    Handles API calls to OpenAI, Anthropic, or custom LLM endpoints
    with consistent error handling and retry logic.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize LLM client with configuration."""
        self.config = config
        self.provider = config.get('provider', 'openai')
        self.model = config.get('model', 'gpt-4')
        self.temperature = config.get('temperature', 0.1)
        self.max_tokens = config.get('max_tokens', 4000)
        self.timeout = config.get('timeout', 60)
        self.retry_attempts = config.get('retry_attempts', 3)
        self.retry_delay = config.get('retry_delay', 1.0)
        
        # Initialize provider-specific clients
        self._init_provider()
    
    def _init_provider(self) -> None:
        """Initialize the specific LLM provider."""
        if self.provider == 'openai':
            api_key = self.config.get('api_key')
            if not api_key:
                raise ValueError("OpenAI API key is required")
            openai.api_key = api_key
            
            # Set organization if provided
            if 'organization' in self.config:
                openai.organization = self.config['organization']
                
        elif self.provider == 'anthropic':
            if not anthropic:
                raise ImportError("anthropic package is required for Anthropic provider")
            api_key = self.config.get('api_key')
            if not api_key:
                raise ValueError("Anthropic API key is required")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
            
        elif self.provider == 'custom':
            self.base_url = self.config.get('base_url')
            if not self.base_url:
                raise ValueError("base_url is required for custom provider")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def generate_completion(self, prompt: str) -> str:
        """
        Generate completion from the LLM.
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            Generated completion text
            
        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self.retry_attempts):
            try:
                if self.provider == 'openai':
                    return self._openai_completion(prompt)
                elif self.provider == 'anthropic':
                    return self._anthropic_completion(prompt)
                elif self.provider == 'custom':
                    return self._custom_completion(prompt)
                    
            except Exception as e:
                logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    def _openai_completion(self, prompt: str) -> str:
        """Generate completion using OpenAI API."""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert knowledge extraction system."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=self.timeout
        )
        return response.choices[0].message.content
    
    def _anthropic_completion(self, prompt: str) -> str:
        """Generate completion using Anthropic API."""
        response = self.anthropic_client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    def _custom_completion(self, prompt: str) -> str:
        """Generate completion using custom API endpoint."""
        headers = {
            'Content-Type': 'application/json',
            **self.config.get('headers', {})
        }
        
        payload = {
            'model': self.model,
            'prompt': prompt,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens
        }
        
        response = requests.post(
            f"{self.base_url}/completions",
            json=payload,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        
        return response.json()['choices'][0]['text']


class DataProcessor:
    """
    Handles loading and preprocessing of various data sources.
    
    Supports text files, PDFs, Word documents, web pages, and other formats
    with appropriate preprocessing for knowledge extraction.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize data processor with configuration."""
        self.config = config
        self.supported_formats = config.get('supported_formats', ['txt', 'md', 'pdf', 'docx', 'html'])
        self.default_encoding = config.get('default_encoding', 'utf-8')
    
    def load_data(self, source: str) -> Tuple[str, Dict[str, Any]]:
        """
        Load data from various sources.
        
        Args:
            source: Path to file or URL
            
        Returns:
            Tuple of (text_content, metadata)
        """
        if source.startswith(('http://', 'https://')):
            return self._load_web_content(source)
        elif os.path.isfile(source):
            return self._load_file_content(source)
        else:
            raise ValueError(f"Unsupported data source: {source}")
    
    def _load_file_content(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Load content from a file."""
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        
        metadata = {
            'source_type': 'file',
            'source_path': file_path,
            'file_extension': file_ext,
            'file_size': os.path.getsize(file_path),
            'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        if file_ext in ['txt', 'md']:
            content = self._load_text_file(file_path)
        elif file_ext == 'pdf':
            content = self._load_pdf_file(file_path)
        elif file_ext == 'docx':
            content = self._load_docx_file(file_path)
        elif file_ext == 'html':
            content = self._load_html_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        return content, metadata
    
    def _load_text_file(self, file_path: str) -> str:
        """Load plain text or markdown file."""
        with open(file_path, 'r', encoding=self.default_encoding) as f:
            return f.read()
    
    def _load_pdf_file(self, file_path: str) -> str:
        """Load PDF file content."""
        text_content = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text_content.append(page.extract_text())
        return '\n'.join(text_content)
    
    def _load_docx_file(self, file_path: str) -> str:
        """Load Word document content."""
        doc = Document(file_path)
        text_content = []
        for paragraph in doc.paragraphs:
            text_content.append(paragraph.text)
        return '\n'.join(text_content)
    
    def _load_html_file(self, file_path: str) -> str:
        """Load HTML file content."""
        with open(file_path, 'r', encoding=self.default_encoding) as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            return soup.get_text()
    
    def _load_web_content(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """Load content from a web URL."""
        web_config = self.config.get('web_scraping', {})
        headers = {
            'User-Agent': web_config.get('user_agent', 'MycoMind/1.0'),
            **web_config.get('headers', {})
        }
        
        response = requests.get(
            url,
            headers=headers,
            timeout=web_config.get('timeout', 30)
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text()
        
        metadata = {
            'source_type': 'web',
            'source_url': url,
            'content_type': response.headers.get('content-type', ''),
            'status_code': response.status_code,
            'retrieved_time': datetime.now().isoformat()
        }
        
        return text_content, metadata
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better extraction quality.
        
        Args:
            text: Raw text content
            
        Returns:
            Preprocessed text
        """
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove null bytes and other problematic characters
        text = text.replace('\x00', '')
        
        # Normalize unicode
        import unicodedata
        text = unicodedata.normalize('NFKD', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Text to chunk
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + chunk_size // 2, end - 200), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks


class MycoMindETL:
    """
    Main ETL pipeline for MycoMind knowledge extraction.
    
    Orchestrates the complete process from data loading through entity
    extraction to Obsidian note generation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the ETL pipeline."""
        # Load configuration
        self.config_manager = load_config(config_path)
        self.config = self.config_manager.config_data
        
        # Initialize components
        self.schema_parser = SchemaParser()
        self.data_processor = DataProcessor(self.config.get('data_sources', {}))
        self.llm_client = LLMClient(self.config.get('llm', {}))
        self.obsidian_generator = create_obsidian_generator(self.config)
        
        # Processing configuration
        self.processing_config = self.config.get('processing', {})
        self.batch_size = self.processing_config.get('batch_size', 5)
        self.enable_caching = self.processing_config.get('enable_caching', True)
        self.cache_ttl = self.processing_config.get('cache_ttl', 3600)
        self.quality_threshold = self.processing_config.get('quality_threshold', 0.7)
        
        # Initialize cache
        self.cache = {}
        if self.enable_caching:
            self._load_cache()
    
    def _load_cache(self) -> None:
        """Load processing cache from disk."""
        cache_dir = self.processing_config.get('cache_directory', '.cache/mycomind')
        cache_file = os.path.join(cache_dir, 'processing_cache.pkl')
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    self.cache = pickle.load(f)
                logger.info(f"Loaded cache with {len(self.cache)} entries")
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")
                self.cache = {}
    
    def _save_cache(self) -> None:
        """Save processing cache to disk."""
        if not self.enable_caching:
            return
        
        cache_dir = self.processing_config.get('cache_directory', '.cache/mycomind')
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, 'processing_cache.pkl')
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
            logger.info(f"Saved cache with {len(self.cache)} entries")
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def _get_cache_key(self, text: str, schema_path: str) -> str:
        """Generate cache key for text and schema combination."""
        content = f"{text}:{schema_path}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def process_data_source(
        self, 
        source: str, 
        schema_path: str,
        output_index: bool = True
    ) -> ProcessingResult:
        """
        Process a complete data source through the ETL pipeline.
        
        Args:
            source: Path to data source (file or URL)
            schema_path: Path to schema definition
            output_index: Whether to create an index note
            
        Returns:
            Processing results
        """
        start_time = time.time()
        
        try:
            # Load and validate schema
            schema_def = self.schema_parser.load_schema(schema_path)
            logger.info(f"Loaded schema: {schema_def.name}")
            
            # Load and preprocess data
            text_content, source_metadata = self.data_processor.load_data(source)
            text_content = self.data_processor.preprocess_text(text_content)
            logger.info(f"Loaded data source: {source} ({len(text_content)} characters)")
            
            # Chunk text if necessary
            chunk_size = self.processing_config.get('chunk_size', 4000)
            chunk_overlap = self.processing_config.get('chunk_overlap', 200)
            chunks = self.data_processor.chunk_text(text_content, chunk_size, chunk_overlap)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Process chunks
            all_entities = []
            all_errors = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i + 1}/{len(chunks)}")
                
                # Check cache first
                cache_key = self._get_cache_key(chunk, schema_path)
                if self.enable_caching and cache_key in self.cache:
                    cached_result = self.cache[cache_key]
                    if time.time() - cached_result['timestamp'] < self.cache_ttl:
                        logger.info(f"Using cached result for chunk {i + 1}")
                        all_entities.extend(cached_result['entities'])
                        continue
                
                # Extract entities from chunk
                chunk_result = self._extract_entities_from_chunk(chunk, schema_def)
                
                if chunk_result.success:
                    all_entities.extend(chunk_result.entities)
                    
                    # Cache the result
                    if self.enable_caching:
                        self.cache[cache_key] = {
                            'entities': chunk_result.entities,
                            'timestamp': time.time()
                        }
                else:
                    all_errors.extend(chunk_result.errors)
            
            # Deduplicate entities
            unique_entities = self._deduplicate_entities(all_entities)
            logger.info(f"Extracted {len(unique_entities)} unique entities")
            
            # Validate entities
            validation_errors = self._validate_entities(unique_entities, schema_def)
            all_errors.extend(validation_errors)
            
            # Filter by quality threshold
            quality_entities = self._filter_by_quality(unique_entities)
            logger.info(f"Filtered to {len(quality_entities)} high-quality entities")
            
            # Generate Obsidian notes
            extraction_metadata = {
                'source_file': source,
                'schema_version': schema_def.version,
                'extraction_date': datetime.now().isoformat(),
                'total_chunks': len(chunks),
                'processing_time': time.time() - start_time
            }
            extraction_metadata.update(source_metadata)
            
            obsidian_results = self.obsidian_generator.process_entities(
                quality_entities, 
                extraction_metadata
            )
            
            # Create index note if requested
            if output_index and quality_entities:
                index_path = self.obsidian_generator.create_index_note(
                    quality_entities, 
                    extraction_metadata
                )
                if index_path:
                    obsidian_results['index_file'] = index_path
            
            # Save cache
            self._save_cache()
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                entities=quality_entities,
                errors=all_errors,
                processing_time=processing_time,
                metadata={
                    'extraction_metadata': extraction_metadata,
                    'obsidian_results': obsidian_results,
                    'schema_info': {
                        'name': schema_def.name,
                        'version': schema_def.version,
                        'entity_types': schema_def.get_entity_names()
                    }
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"ETL processing failed: {e}")
            return ProcessingResult(
                success=False,
                entities=[],
                errors=[str(e)],
                processing_time=processing_time,
                metadata={}
            )
    
    def _extract_entities_from_chunk(
        self, 
        text_chunk: str, 
        schema_def: SchemaDefinition
    ) -> ProcessingResult:
        """Extract entities from a single text chunk."""
        try:
            # Build extraction prompt
            schema_prompt = self.schema_parser.build_extraction_prompt(schema_def)
            
            extraction_prompt = f"""
You are an expert knowledge extraction system. Extract structured information from the provided text according to the given schema.

{schema_prompt}

EXTRACTION RULES:
1. Extract only information explicitly present in the text
2. Use exact entity names when creating WikiLinks: [[Entity Name]]
3. Maintain consistency in entity naming across extractions
4. Include confidence scores for uncertain extractions (0.0 to 1.0)
5. Preserve important context and relationships
6. Format relationship values as WikiLinks: "[[Entity Name]]"

INPUT TEXT:
{text_chunk}

OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
  "entities": [
    {{
      "type": "EntityType",
      "properties": {{
        "name": "Entity Name",
        "description": "Entity description",
        ...
      }},
      "relationships": {{
        "relationshipName": "[[Target Entity]]",
        "multipleRelationships": ["[[Entity1]]", "[[Entity2]]"]
      }},
      "confidence": 0.95,
      "source_context": "relevant text snippet"
    }}
  ],
  "metadata": {{
    "extraction_date": "{datetime.now().isoformat()}",
    "schema_version": "{schema_def.version}",
    "processing_notes": "any relevant notes"
  }}
}}

Ensure the JSON is valid and properly formatted.
"""
            
            # Get LLM response
            response = self.llm_client.generate_completion(extraction_prompt)
            
            # Parse JSON response
            try:
                result_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response from LLM: {e}")
                return ProcessingResult(
                    success=False,
                    entities=[],
                    errors=[f"Invalid JSON response: {e}"],
                    processing_time=0,
                    metadata={}
                )
            
            # Extract entities
            entities = result_data.get('entities', [])
            
            # Validate each entity
            validated_entities = []
            validation_errors = []
            
            for entity in entities:
                is_valid, errors = self.schema_parser.validate_extracted_entity(entity, schema_def)
                if is_valid:
                    validated_entities.append(entity)
                else:
                    validation_errors.extend(errors)
            
            return ProcessingResult(
                success=True,
                entities=validated_entities,
                errors=validation_errors,
                processing_time=0,
                metadata=result_data.get('metadata', {})
            )
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return ProcessingResult(
                success=False,
                entities=[],
                errors=[str(e)],
                processing_time=0,
                metadata={}
            )
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities based on type and name."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            entity_type = entity.get('type', '')
            entity_name = entity.get('properties', {}).get('name', '')
            key = (entity_type, entity_name)
            
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
            else:
                logger.debug(f"Skipping duplicate entity: {entity_type} - {entity_name}")
        
        return unique_entities
    
    def _validate_entities(
        self, 
        entities: List[Dict[str, Any]], 
        schema_def: SchemaDefinition
    ) -> List[str]:
        """Validate entities against schema and cross-references."""
        errors = []
        
        # Validate WikiLinks
        wikilink_errors = self.obsidian_generator.validate_wikilinks(entities)
        errors.extend(wikilink_errors)
        
        return errors
    
    def _filter_by_quality(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entities by quality threshold."""
        quality_entities = []
        
        for entity in entities:
            confidence = entity.get('confidence', 1.0)
            if confidence >= self.quality_threshold:
                quality_entities.append(entity)
            else:
                entity_name = entity.get('properties', {}).get('name', 'Unknown')
                logger.debug(f"Filtered low-quality entity: {entity_name} (confidence: {confidence})")
        
        return quality_entities


def main():
    """Main entry point for the ETL pipeline."""
    parser = argparse.ArgumentParser(description='MycoMind Knowledge Extraction ETL Pipeline')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--schema', '-s', required=True, help='Path to schema file')
    parser.add_argument('--source', required=True, help='Path to data source (file or URL)')
    parser.add_argument('--no-index', action='store_true', help='Skip creating index note')
    parser.add_argument('--dry-run', action='store_true', help='Validate configuration without processing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize ETL pipeline
        etl = MycoMindETL(args.config)
        
        if args.dry_run:
            logger.info("Dry run mode - validating configuration")
            logger.info(f"Configuration loaded: {etl.config_manager.config_path}")
            logger.info(f"Schema file: {args.schema}")
            logger.info(f"Data source: {args.source}")
            logger.info("Configuration validation successful")
            return 0
        
        # Process data source
        logger.info("Starting ETL processing")
        result = etl.process_data_source(
            source=args.source,
            schema_path=args.schema,
            output_index=not args.no_index
        )
        
        # Report results
        if result.success:
            logger.info("ETL processing completed successfully")
            logger.info(f"Extracted {len(result.entities)} entities")
            logger.info(f"Processing time: {result.processing_time:.2f} seconds")
            
            obsidian_results = result.metadata.get('obsidian_results', {})
            logger.info(f"Generated {len(obsidian_results.get('generated_files', []))} notes")
            
            if obsidian_results.get('skipped_files'):
                logger.warning(f"Skipped {len(obsidian_results['skipped_files'])} existing files")
            
            if result.errors:
                logger.warning(f"Processing completed with {len(result.errors)} warnings:")
                for error in result.errors[:5]:  # Show first 5 errors
                    logger.warning(f"  - {error}")
                if len(result.errors) > 5:
                    logger.warning(f"  ... and {len(result.errors) - 5} more")
            
            return 0
        else:
            logger.error("ETL processing failed")
            for error in result.errors:
                logger.error(f"  - {error}")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
