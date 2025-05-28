"""
Configuration Manager for MycoMind

This module handles loading, validating, and managing configuration settings
for the MycoMind knowledge extraction system. It supports environment variables,
configuration inheritance, and validation against JSON schemas.

Future Enhancement: This module will be extended to support the automated
generation of the project's knowledge graph via a future build_project_kg.py
script that will parse this and other modules to create graph representations.
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import yaml
from jsonschema import validate, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    message: str
    errors: List[str]


class ConfigManager:
    """
    Centralized configuration management for MycoMind.
    
    Handles loading configuration from JSON files, environment variables,
    and provides validation and access methods for other system components.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the main configuration file
        """
        self.config_path = config_path or "config.json"
        self.config_data: Dict[str, Any] = {}
        self.schema_cache: Dict[str, Dict[str, Any]] = {}
        
        # Default configuration schema
        self.config_schema = {
            "type": "object",
            "required": ["llm", "obsidian"],
            "properties": {
                "version": {"type": "string"},
                "profile": {"type": "string"},
                "llm": {
                    "type": "object",
                    "required": ["provider", "model"],
                    "properties": {
                        "provider": {"type": "string", "enum": ["openai", "anthropic", "custom"]},
                        "model": {"type": "string"},
                        "api_key_env": {"type": "string"},
                        "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                        "max_tokens": {"type": "integer", "minimum": 1}
                    }
                },
                "obsidian": {
                    "type": "object",
                    "required": ["vault_path"],
                    "properties": {
                        "vault_path": {"type": "string"},
                        "notes_folder": {"type": "string"},
                        "folder_structure": {"type": "string", "enum": ["flat", "by_type", "by_date", "by_source", "custom"]}
                    }
                }
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file and environment variables.
        
        Returns:
            The loaded and validated configuration
            
        Raises:
            ConfigValidationError: If configuration is invalid
            FileNotFoundError: If configuration file doesn't exist
        """
        try:
            # Load base configuration
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            
            # Handle configuration inheritance
            if "extends" in self.config_data:
                base_config = self._load_base_config(self.config_data["extends"])
                self.config_data = self._merge_configs(base_config, self.config_data)
            
            # Resolve environment variables
            self.config_data = self._resolve_environment_variables(self.config_data)
            
            # Validate configuration
            self._validate_config()
            
            # Set up logging based on configuration
            self._setup_logging()
            
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config_data
            
        except json.JSONDecodeError as e:
            raise ConfigValidationError(
                f"Invalid JSON in configuration file: {self.config_path}",
                [str(e)]
            )
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _load_base_config(self, base_path: str) -> Dict[str, Any]:
        """Load base configuration for inheritance."""
        if not os.path.exists(base_path):
            raise FileNotFoundError(f"Base configuration file not found: {base_path}")
        
        with open(base_path, 'r') as f:
            return json.load(f)
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge configuration dictionaries with override taking precedence.
        
        Args:
            base: Base configuration
            override: Override configuration
            
        Returns:
            Merged configuration
        """
        merged = base.copy()
        
        for key, value in override.items():
            if key == "extends":
                continue  # Skip the extends directive
            
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _resolve_environment_variables(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve environment variable references in configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Configuration with environment variables resolved
        """
        def resolve_value(value):
            if isinstance(value, str):
                # Handle environment variable references
                if value.endswith('_env'):
                    env_var = value[:-4]  # Remove '_env' suffix
                    return os.getenv(env_var)
                return value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            return value
        
        resolved_config = {}
        for key, value in config.items():
            if key.endswith('_env'):
                # This is an environment variable reference
                env_var_name = value
                env_value = os.getenv(env_var_name)
                if env_value is None:
                    logger.warning(f"Environment variable {env_var_name} not found")
                # Store the actual value with the key without '_env' suffix
                actual_key = key[:-4]
                resolved_config[actual_key] = env_value
            else:
                resolved_config[key] = resolve_value(value)
        
        return resolved_config
    
    def _validate_config(self) -> None:
        """
        Validate configuration against schema.
        
        Raises:
            ConfigValidationError: If validation fails
        """
        try:
            validate(instance=self.config_data, schema=self.config_schema)
            
            # Additional custom validations
            errors = []
            
            # Validate LLM configuration
            llm_config = self.config_data.get("llm", {})
            if llm_config.get("provider") == "openai" and not llm_config.get("api_key"):
                errors.append("OpenAI API key is required when using OpenAI provider")
            
            # Validate Obsidian configuration
            obsidian_config = self.config_data.get("obsidian", {})
            vault_path = obsidian_config.get("vault_path")
            if vault_path and not os.path.exists(vault_path):
                logger.warning(f"Obsidian vault path does not exist: {vault_path}")
            
            if errors:
                raise ConfigValidationError("Configuration validation failed", errors)
                
        except ValidationError as e:
            raise ConfigValidationError(
                "Configuration schema validation failed",
                [e.message]
            )
    
    def _setup_logging(self) -> None:
        """Set up logging based on configuration."""
        logging_config = self.config_data.get("logging", {})
        
        # Set log level
        log_level = logging_config.get("level", "INFO")
        logging.getLogger().setLevel(getattr(logging, log_level.upper()))
        
        # Configure log format
        log_format = logging_config.get(
            "format", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # Set up file logging if specified
        log_file = logging_config.get("file")
        if log_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(file_handler)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'llm.model')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM-specific configuration."""
        return self.config_data.get("llm", {})
    
    def get_obsidian_config(self) -> Dict[str, Any]:
        """Get Obsidian-specific configuration."""
        return self.config_data.get("obsidian", {})
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Get processing-specific configuration."""
        return self.config_data.get("processing", {})
    
    def save_config(self, path: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            path: Path to save configuration (defaults to original path)
        """
        save_path = path or self.config_path
        
        with open(save_path, 'w') as f:
            json.dump(self.config_data, f, indent=2)
        
        logger.info(f"Configuration saved to {save_path}")
    
    def validate_schema_file(self, schema_path: str) -> bool:
        """
        Validate a schema file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            with open(schema_path, 'r') as f:
                schema = json.load(f)
            
            # Basic validation of schema structure
            required_fields = ["@context", "entities"]
            for field in required_fields:
                if field not in schema:
                    logger.error(f"Schema missing required field: {field}")
                    return False
            
            # Cache the schema for later use
            self.schema_cache[schema_path] = schema
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed for {schema_path}: {e}")
            return False
    
    def get_schema(self, schema_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached schema or load from file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Schema dictionary or None if not found
        """
        if schema_path in self.schema_cache:
            return self.schema_cache[schema_path]
        
        if self.validate_schema_file(schema_path):
            return self.schema_cache[schema_path]
        
        return None
    
    def create_default_config(self, path: str) -> None:
        """
        Create a default configuration file.
        
        Args:
            path: Path where to create the configuration file
        """
        default_config = {
            "version": "1.0.0",
            "profile": "default",
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "api_key_env": "OPENAI_API_KEY",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60,
                "retry_attempts": 3,
                "retry_delay": 1.0
            },
            "obsidian": {
                "vault_path": "/path/to/your/obsidian/vault",
                "notes_folder": "extracted_knowledge",
                "create_folders": True,
                "folder_structure": "by_type",
                "filename_template": "{name}",
                "overwrite_existing": False,
                "backup_existing": True
            },
            "processing": {
                "batch_size": 5,
                "max_concurrent": 3,
                "chunk_size": 4000,
                "chunk_overlap": 200,
                "enable_caching": True,
                "cache_ttl": 3600,
                "quality_threshold": 0.7
            },
            "logging": {
                "level": "INFO",
                "file": "logs/mycomind.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        with open(path, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        logger.info(f"Default configuration created at {path}")


def load_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Convenience function to load configuration.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configured ConfigManager instance
    """
    manager = ConfigManager(config_path)
    manager.load_config()
    return manager


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-default":
            config_path = sys.argv[2] if len(sys.argv) > 2 else "config.json"
            manager = ConfigManager()
            manager.create_default_config(config_path)
            print(f"Default configuration created at {config_path}")
        elif sys.argv[1] == "validate":
            config_path = sys.argv[2] if len(sys.argv) > 2 else "config.json"
            try:
                manager = load_config(config_path)
                print("Configuration is valid!")
            except Exception as e:
                print(f"Configuration validation failed: {e}")
                sys.exit(1)
    else:
        print("Usage:")
        print("  python config_manager.py create-default [path]")
        print("  python config_manager.py validate [path]")
