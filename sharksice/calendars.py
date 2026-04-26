#!/usr/bin/env python3
"""
Standalone script to generate calendar files from stored events in SQLite.
"""

import logging
import asyncio
import sqlite3
import json
import pathlib
from dataclasses import dataclass
from typing import Set

import ics
from ics.types import ArrowLike

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log', mode='a'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = pathlib.Path(__file__).parent.parent / "events.db"
CALENDARS_DIR = pathlib.Path(__file__).parent.parent / "data" / "calendars"


@dataclass(frozen=True)
class Event:
    name: str
    begin: ArrowLike
    end: ArrowLike
    description: str
    location: str
    url: str

    def to_ics_event(self) -> ics.Event:
        return ics.Event(
            name=self.name,
            begin=self.begin,
            end=self.end,
            description=self.description,
            url=self.url,
            location=self.location
        )


def get_events_by_partition(partition_keys: list) -> list:
    """Query events from SQLite by partition keys."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(partition_keys))
        cursor.execute(f'''
            SELECT * FROM events
            WHERE partition_key IN ({placeholders})
            ORDER BY start_date
        ''', partition_keys)
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Error querying events: {e}", exc_info=True)
        return []


async def generate_and_save_calendars():
    """Generate calendar files from events and save locally."""
    try:
        calendars_file = pathlib.Path(__file__).parent.parent / "configs" / "calendars.json"
        if not calendars_file.exists():
            logger.error(f"calendars.json not found at {calendars_file}")
            return False
        
        # Create calendars directory if it doesn't exist
        CALENDARS_DIR.mkdir(parents=True, exist_ok=True)
        
        calendars = json.loads(calendars_file.read_text())
        
        for calendar in calendars:
            try:
                _calendar = ics.Calendar(creator="Sharks Ice Unofficial Calendar", calendar_name=calendar['name'])
                partition_keys = calendar.get("keys", [])
                
                logger.info(f"Generating calendar for {calendar['name']} with keys: {partition_keys}")
                
                events: Set[Event] = set()
                
                # Query events from SQLite
                rows = get_events_by_partition(partition_keys)
                logger.info(f"Found {len(rows)} events for {calendar['name']}")
                
                for row in rows:
                    logger.info(f"Adding event {row.get('product_name')} on {row.get('start_date')}")
                    events.add(Event(
                        name=row.get("product_name", ""),
                        begin=row.get("start_date"),
                        end=row.get("end_date"),
                        description=row.get("description", ""),
                        location=row.get("address", ""),
                        url="https://apps.daysmartrecreation.com/dash/x/#/online/sharks/event-registration"
                    ))
                
                _calendar.events = [event.to_ics_event() for event in events]
                
                # Save calendar to file
                calendar_path = CALENDARS_DIR / f"{calendar['name']}.ics"
                calendar_path.write_text(_calendar.serialize())
                
                logger.info(f"Successfully saved calendar for {calendar['name']} with {len(events)} events to {calendar_path}")
            
            except Exception as e:
                logger.error(f"Error processing calendar {calendar.get('name')}: {e}", exc_info=True)
                return False
        
        logger.info(f"Calendar generation completed successfully. Files saved to {CALENDARS_DIR}")
        return True
    
    except Exception as e:
        logger.error(f"Error in generate_and_save_calendars: {e}", exc_info=True)
        return False


async def main():
    """Main entry point."""
    success = await generate_and_save_calendars()
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
