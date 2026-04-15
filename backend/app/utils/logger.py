import sys
from loguru import logger

def setup_logging(log_level: str = "INFO"):
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
    )
    logger.add(
        "../logs/empathy_engine.log",
        rotation="500 MB",
        retention="10 days",
        level="DEBUG",
        compression="zip"
    )

# Initialize logging
setup_logging()
