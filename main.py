"""
ADITIM Monitor - Main Application Entry Point
"""

import asyncio
import logging
from pathlib import Path

from src.config.settings import Settings
from src.core.engine import MonitoringEngine


def setup_logging(config: Settings) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, config.logging.level.upper()),
        format=config.logging.format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.logging.file_path)
        ]
    )


async def main() -> None:
    """Main application entry point."""
    # Load configuration
    config = Settings.from_yaml("config/default.yaml")
    
    # Setup logging
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ADITIM Monitor...")
    
    # Initialize monitoring engine
    engine = MonitoringEngine(config)
    
    try:
        # Start monitoring
        await engine.start()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        await engine.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
