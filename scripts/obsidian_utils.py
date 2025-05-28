"""
Obsidian Utilities for MycoMind

This module handles the generation of Obsidian-compatible Markdown files
with YAML frontmatter, WikiLinks, and proper file organization. It provides
utilities for creating structured notes from extracted entities and managing
the output file system.

Future Enhancement: This module will be parsed by the future build_project_kg.py
script to understand how the system generates its output format, contributing
to the project's self-documenting knowledge graph.
"""

import os
import re
import yaml
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import unicodedata
import shutil

logger = logging.getLogger(__name__)


class ObsidianUtilsError(Exception):
    """Raised when Obsidian utilities encounter an error."""
    pass


class ObsidianNoteGenerator:
    """
    Generator for Obsidian-compatible Markdown notes with YAML frontmatter.
    
    Handles the creation of structured notes from extracted entities,
    including proper WikiLink formatting, file organization, and metadata
    management for integration with Obsidian vaults.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Obsidian note generator.
        
        Args:
            config: Configuration dictionary containing Obsidian settings
        """
        self.config = config
        self.vault_path = config.get('vault_path', '')
        self.notes_folder = config.get('notes_folder', 'extracted_knowledge')
        self.folder_structure = config.get('folder_structure', 'by_type')
        self.filename_template = config.get('filename_template', '{name}')
        self.overwrite_existing = config.get('overwrite_existing', False)
        self.backup_existing = config.get('backup_existing', True)
        self.create_folders = config.get('create_folders', True)
        
        # Validate configuration
        self._validate_config()
        
        # Initialize folder mapping for custom structure
        self.folder_mapping = config.get('folder_mapping', {})
        
        # Track generated files for reporting
        self.generated_files: List[str] = []
        self.skipped_files: List[str] = []
        self.backed_up_files: List[str] = []
    
    def _validate_config(self) -> None:
        """Validate Obsidian configuration."""
        if not self.vault_path:
            raise ObsidianUtilsError("Obsidian vault_path is required")
        
        if not os.path.exists(self.vault_path):
            logger.warning(f"Obsidian vault path does not exist: {self.vault_path}")
    
    def generate_note(
        self, 
        entity: Dict[str, Any], 
        metadata: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Generate a complete Obsidian note from an entity.
        
        Args:
            entity: Entity data with type, properties, and relationships
            metadata: Additional metadata about the extraction
            
        Returns:
            Tuple of (file_path, note_content)
        """
        # Generate YAML frontmatter
        frontmatter = self._create_frontmatter(entity, metadata)
        
        # Generate main content
        content = self._create_content(entity, metadata)
        
        # Combine frontmatter and content
        note_content = f"---\n{frontmatter}---\n\n{content}"
        
        # Determine file path
        file_path = self._get_file_path(entity)
        
        return file_path, note_content
    
    def _create_frontmatter(self, entity: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """
        Create YAML frontmatter for the note.
        
        Args:
            entity: Entity data
            metadata: Extraction metadata
            
        Returns:
            YAML frontmatter as string
        """
        frontmatter_data = {}
        
        # Add entity type
        if 'type' in entity:
            frontmatter_data['type'] = entity['type']
        
        # Add entity properties
        properties = entity.get('properties', {})
        for prop_name, prop_value in properties.items():
            # Handle special formatting for certain property types
            if isinstance(prop_value, list):
                frontmatter_data[prop_name] = prop_value
            elif isinstance(prop_value, dict):
                frontmatter_data[prop_name] = prop_value
            else:
                frontmatter_data[prop_name] = str(prop_value)
        
        # Add relationships with WikiLink formatting
        relationships = entity.get('relationships', {})
        for rel_name, rel_targets in relationships.items():
            if isinstance(rel_targets, list):
                frontmatter_data[rel_name] = rel_targets
            else:
                frontmatter_data[rel_name] = rel_targets
        
        # Add extraction metadata
        frontmatter_data['created'] = datetime.now().isoformat()
        frontmatter_data['source'] = metadata.get('source_file', 'unknown')
        frontmatter_data['extraction_date'] = metadata.get('extraction_date', datetime.now().isoformat())
        
        if 'confidence' in entity:
            frontmatter_data['extraction_confidence'] = entity['confidence']
        
        if 'schema_version' in metadata:
            frontmatter_data['schema_version'] = metadata['schema_version']
        
        # Add tags
        tags = self._generate_tags(entity)
        if tags:
            frontmatter_data['tags'] = tags
        
        # Convert to YAML
        return yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
    
    def _create_content(self, entity: Dict[str, Any], metadata: Dict[str, Any]) -> str:
        """
        Create the main content of the note.
        
        Args:
            entity: Entity data
            metadata: Extraction metadata
            
        Returns:
            Markdown content as string
        """
        content_parts = []
        
        # Title
        name = entity.get('properties', {}).get('name', 'Unnamed Entity')
        content_parts.append(f"# {name}")
        
        # Description or summary
        description = entity.get('properties', {}).get('description')
        if description:
            content_parts.append(f"\n{description}")
        
        # Source context if available
        if 'source_context' in entity:
            content_parts.append(f"\n## Source Context\n\n> {entity['source_context']}")
        
        # Properties section
        properties = entity.get('properties', {})
        if properties:
            content_parts.append("\n## Properties")
            for prop_name, prop_value in properties.items():
                if prop_name not in ['name', 'description']:  # Skip already displayed properties
                    formatted_name = prop_name.replace('_', ' ').title()
                    if isinstance(prop_value, list):
                        value_str = ', '.join(str(v) for v in prop_value)
                    else:
                        value_str = str(prop_value)
                    content_parts.append(f"- **{formatted_name}**: {value_str}")
        
        # Relationships section
        relationships = entity.get('relationships', {})
        if relationships:
            content_parts.append("\n## Relationships")
            for rel_name, rel_targets in relationships.items():
                formatted_rel = rel_name.replace('_', ' ').title()
                if isinstance(rel_targets, list):
                    target_list = ", ".join(rel_targets)
                else:
                    target_list = rel_targets
                content_parts.append(f"- **{formatted_rel}**: {target_list}")
        
        # Metadata section
        content_parts.append("\n## Metadata")
        content_parts.append(f"- **Extracted**: {metadata.get('extraction_date', 'Unknown')}")
        content_parts.append(f"- **Source**: {metadata.get('source_file', 'Unknown')}")
        
        if 'confidence' in entity:
            confidence = entity['confidence']
            content_parts.append(f"- **Confidence**: {confidence:.2f}")
        
        # Add backlinks section placeholder
        content_parts.append("\n## Backlinks\n\n*This section will be automatically populated by Obsidian.*")
        
        return "\n".join(content_parts)
    
    def _generate_tags(self, entity: Dict[str, Any]) -> List[str]:
        """
        Generate appropriate tags for the entity.
        
        Args:
            entity: Entity data
            
        Returns:
            List of tags
        """
        tags = []
        
        # Add entity type as tag
        entity_type = entity.get('type')
        if entity_type:
            tags.append(entity_type.lower())
        
        # Add domain-specific tags based on properties
        properties = entity.get('properties', {})
        
        # Add tags based on common properties
        if 'domain' in properties:
            domain = properties['domain']
            if isinstance(domain, str):
                tags.append(f"domain/{domain.lower().replace(' ', '-')}")
        
        if 'industry' in properties:
            industry = properties['industry']
            if isinstance(industry, str):
                tags.append(f"industry/{industry.lower().replace(' ', '-')}")
        
        if 'expertise' in properties:
            expertise = properties['expertise']
            if isinstance(expertise, list):
                for skill in expertise:
                    if isinstance(skill, str):
                        tags.append(f"expertise/{skill.lower().replace(' ', '-')}")
        
        # Add extraction tag
        tags.append('mycomind-extracted')
        
        return tags
    
    def _get_file_path(self, entity: Dict[str, Any]) -> str:
        """
        Determine the file path for the entity note.
        
        Args:
            entity: Entity data
            
        Returns:
            Full file path for the note
        """
        # Get entity name and type
        entity_name = entity.get('properties', {}).get('name', 'Unnamed Entity')
        entity_type = entity.get('type', 'Unknown')
        
        # Generate filename
        filename = self._generate_filename(entity_name, entity_type, entity)
        
        # Determine folder path
        folder_path = self._get_folder_path(entity_type)
        
        # Combine paths
        full_path = os.path.join(self.vault_path, folder_path, filename)
        
        return full_path
    
    def _generate_filename(self, entity_name: str, entity_type: str, entity: Dict[str, Any]) -> str:
        """
        Generate a safe filename for the entity.
        
        Args:
            entity_name: Name of the entity
            entity_type: Type of the entity
            entity: Full entity data
            
        Returns:
            Safe filename with .md extension
        """
        # Prepare template variables
        template_vars = {
            'name': entity_name,
            'type': entity_type,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': str(int(datetime.now().timestamp())),
            'source': 'unknown'  # Could be enhanced with actual source info
        }
        
        # Apply filename template
        try:
            filename = self.filename_template.format(**template_vars)
        except KeyError as e:
            logger.warning(f"Invalid filename template variable: {e}")
            filename = entity_name
        
        # Sanitize filename
        filename = self._sanitize_filename(filename)
        
        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename += '.md'
        
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.
        
        Args:
            filename: Raw filename
            
        Returns:
            Sanitized filename
        """
        # Normalize unicode characters
        filename = unicodedata.normalize('NFKD', filename)
        
        # Remove or replace problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
        
        # Replace spaces based on configuration
        filename_config = self.config.get('filename_sanitization', {})
        if filename_config.get('replace_spaces'):
            replacement = filename_config.get('replace_spaces', '_')
            filename = filename.replace(' ', replacement)
        
        # Remove special characters if configured
        if filename_config.get('remove_special_chars', False):
            filename = re.sub(r'[^\w\s\-_.]', '', filename)
        
        # Apply case transformation
        case_setting = filename_config.get('case')
        if case_setting == 'lower':
            filename = filename.lower()
        elif case_setting == 'upper':
            filename = filename.upper()
        
        # Limit length
        max_length = filename_config.get('max_length', 100)
        if len(filename) > max_length:
            # Keep the extension
            name_part, ext = os.path.splitext(filename)
            filename = name_part[:max_length - len(ext)] + ext
        
        # Ensure filename is not empty
        if not filename or filename == '.md':
            filename = 'unnamed_entity.md'
        
        return filename
    
    def _get_folder_path(self, entity_type: str) -> str:
        """
        Determine the folder path for an entity type.
        
        Args:
            entity_type: Type of the entity
            
        Returns:
            Relative folder path within the vault
        """
        base_folder = self.notes_folder
        
        if self.folder_structure == 'flat':
            return base_folder
        elif self.folder_structure == 'by_type':
            return os.path.join(base_folder, entity_type.lower())
        elif self.folder_structure == 'by_date':
            date_folder = datetime.now().strftime('%Y-%m-%d')
            return os.path.join(base_folder, date_folder)
        elif self.folder_structure == 'by_source':
            # Could be enhanced with actual source information
            return os.path.join(base_folder, 'unknown_source')
        elif self.folder_structure == 'custom':
            mapped_folder = self.folder_mapping.get(entity_type, entity_type.lower())
            return os.path.join(base_folder, mapped_folder)
        else:
            logger.warning(f"Unknown folder structure: {self.folder_structure}")
            return base_folder
    
    def save_note(self, file_path: str, content: str) -> bool:
        """
        Save a note to the filesystem.
        
        Args:
            file_path: Full path where to save the note
            content: Note content
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if self.create_folders and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Check if file already exists
            if os.path.exists(file_path):
                if not self.overwrite_existing:
                    logger.warning(f"File already exists, skipping: {file_path}")
                    self.skipped_files.append(file_path)
                    return False
                
                # Backup existing file if configured
                if self.backup_existing:
                    backup_path = self._create_backup(file_path)
                    if backup_path:
                        self.backed_up_files.append(backup_path)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.generated_files.append(file_path)
            logger.info(f"Note saved: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save note {file_path}: {e}")
            return False
    
    def _create_backup(self, file_path: str) -> Optional[str]:
        """
        Create a backup of an existing file.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file, or None if backup failed
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{file_path}.backup_{timestamp}"
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            return None
    
    def process_entities(
        self, 
        entities: List[Dict[str, Any]], 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process multiple entities and generate notes.
        
        Args:
            entities: List of entity data
            metadata: Extraction metadata
            
        Returns:
            Summary of processing results
        """
        results = {
            'total_entities': len(entities),
            'generated_files': [],
            'skipped_files': [],
            'backed_up_files': [],
            'errors': []
        }
        
        # Reset tracking lists
        self.generated_files = []
        self.skipped_files = []
        self.backed_up_files = []
        
        for entity in entities:
            try:
                file_path, content = self.generate_note(entity, metadata)
                success = self.save_note(file_path, content)
                
                if not success and file_path not in self.skipped_files:
                    results['errors'].append(f"Failed to save: {file_path}")
                    
            except Exception as e:
                entity_name = entity.get('properties', {}).get('name', 'Unknown')
                error_msg = f"Error processing entity '{entity_name}': {e}"
                results['errors'].append(error_msg)
                logger.error(error_msg)
        
        # Update results
        results['generated_files'] = self.generated_files.copy()
        results['skipped_files'] = self.skipped_files.copy()
        results['backed_up_files'] = self.backed_up_files.copy()
        
        # Log summary
        logger.info(f"Processing complete: {len(self.generated_files)} files generated, "
                   f"{len(self.skipped_files)} skipped, {len(results['errors'])} errors")
        
        return results
    
    def validate_wikilinks(self, entities: List[Dict[str, Any]]) -> List[str]:
        """
        Validate that WikiLinks reference existing entities.
        
        Args:
            entities: List of entity data
            
        Returns:
            List of validation errors
        """
        errors = []
        entity_names = {e.get('properties', {}).get('name') for e in entities if e.get('properties', {}).get('name')}
        
        for entity in entities:
            entity_name = entity.get('properties', {}).get('name', 'Unknown')
            relationships = entity.get('relationships', {})
            
            for rel_name, rel_targets in relationships.items():
                if isinstance(rel_targets, list):
                    targets = rel_targets
                else:
                    targets = [rel_targets]
                
                for target in targets:
                    if isinstance(target, str) and target.startswith('[[') and target.endswith(']]'):
                        target_name = target[2:-2]  # Remove [[ and ]]
                        if target_name not in entity_names:
                            errors.append(f"Unresolved WikiLink in '{entity_name}': {target}")
        
        return errors
    
    def create_index_note(self, entities: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """
        Create an index note that links to all generated entities.
        
        Args:
            entities: List of entity data
            metadata: Extraction metadata
            
        Returns:
            Path to the created index note
        """
        # Group entities by type
        entities_by_type = {}
        for entity in entities:
            entity_type = entity.get('type', 'Unknown')
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)
        
        # Create index content
        content_parts = [
            "# Knowledge Extraction Index",
            f"\nGenerated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Source: {metadata.get('source_file', 'Unknown')}",
            f"Total entities: {len(entities)}\n"
        ]
        
        # Add sections for each entity type
        for entity_type, type_entities in sorted(entities_by_type.items()):
            content_parts.append(f"## {entity_type} ({len(type_entities)})\n")
            
            for entity in sorted(type_entities, key=lambda e: e.get('properties', {}).get('name', '')):
                entity_name = entity.get('properties', {}).get('name', 'Unnamed')
                content_parts.append(f"- [[{entity_name}]]")
            
            content_parts.append("")  # Empty line between sections
        
        # Add metadata section
        content_parts.extend([
            "## Extraction Metadata",
            f"- **Schema Version**: {metadata.get('schema_version', 'Unknown')}",
            f"- **Extraction Date**: {metadata.get('extraction_date', 'Unknown')}",
            f"- **Generated Files**: {len(self.generated_files)}",
            f"- **Skipped Files**: {len(self.skipped_files)}"
        ])
        
        # Create index file
        index_content = "\n".join(content_parts)
        index_filename = f"extraction_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        index_path = os.path.join(self.vault_path, self.notes_folder, index_filename)
        
        # Save index note
        if self.save_note(index_path, index_content):
            logger.info(f"Index note created: {index_path}")
            return index_path
        else:
            logger.error("Failed to create index note")
            return ""


def create_obsidian_generator(config: Dict[str, Any]) -> ObsidianNoteGenerator:
    """
    Factory function to create an ObsidianNoteGenerator.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Configured ObsidianNoteGenerator instance
    """
    obsidian_config = config.get('obsidian', {})
    return ObsidianNoteGenerator(obsidian_config)


if __name__ == "__main__":
    # Example usage and testing
    import sys
    import json
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Test configuration
        test_config = {
            'vault_path': '/tmp/test_vault',
            'notes_folder': 'test_extraction',
            'folder_structure': 'by_type',
            'filename_template': '{name}',
            'create_folders': True
        }
        
        # Create test directory
        os.makedirs('/tmp/test_vault/test_extraction', exist_ok=True)
        
        # Test entity
        test_entity = {
            'type': 'Person',
            'properties': {
                'name': 'John Doe',
                'email': 'john@example.com',
                'role': 'Software Engineer'
            },
            'relationships': {
                'worksFor': '[[Acme Corp]]',
                'knows': ['[[Jane Smith]]', '[[Bob Johnson]]']
            },
            'confidence': 0.95
        }
        
        test_metadata = {
            'source_file': 'test_document.txt',
            'extraction_date': datetime.now().isoformat(),
            'schema_version': '1.0.0'
        }
        
        # Generate note
        generator = ObsidianNoteGenerator(test_config)
        file_path, content = generator.generate_note(test_entity, test_metadata)
        
        print(f"Generated file path: {file_path}")
        print("\nGenerated content:")
        print("=" * 50)
        print(content)
        
        # Save the note
        success = generator.save_note(file_path, content)
        print(f"\nSave successful: {success}")
        
    else:
        print("Usage:")
        print("  python obsidian_utils.py test")
