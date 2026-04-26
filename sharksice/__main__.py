import asyncio

from .calendars import generate_and_save_calendars
from .events import fetch_and_store_events

async def main():
    """Main entry point."""
    success = await fetch_and_store_events()
    success = await generate_and_save_calendars()
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())