import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger('config')


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to config.json (defaults to ./config.json)

    Returns:
        Configuration dictionary (empty if file not found)
    """
    if config_path is None:
        # Default to config.json in project root
        config_path = Path(__file__).parent.parent.parent / 'config.json'

    if not config_path.exists():
        logger.info(f"No config file found at {config_path}, using defaults")
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        logger.info(f"Loaded config from {config_path}")
        return config

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


def get_messaging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract messaging configuration section."""
    return config.get('messaging', {})
