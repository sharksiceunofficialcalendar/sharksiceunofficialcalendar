import asyncio
import os
import logging

from .calendars import generate_and_save_calendars
from .events import fetch_and_store_events

async def main():
    """Main entry point."""
    logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log', mode='a'),
        logging.StreamHandler()
    ]
)
    logger = logging.getLogger(__name__)
    logger.info("Start fetch_and_store_events")
    success = await fetch_and_store_events()
    logger.info(f"result of fetch_and_store_events {success}")
    if not success:
        os.exit(1)
    logger.info("Start generate_and_save_calendars")
    success = await generate_and_save_calendars()
    logger.info(f"result of generate_and_save_calendars {success}")
    if not success:
        os.exit(1)


if __name__ == "__main__":
    asyncio.run(main())