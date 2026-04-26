import logging
import asyncio
import sqlite3
import json
import pathlib
from dataclasses import dataclass
from typing import Set

from datetime import datetime
from dateutil import parser as dateutil_parser
from icalendar import Calendar, Event as IcalendarEvent

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
class CalendarEvent:
    name: str
    begin: datetime
    end: datetime
    description: str
    location: str
    url: str

    def to_icalendar_event(self) -> IcalendarEvent:
        event = IcalendarEvent()
        event.add('summary', self.name)
        event.add('dtstart', self.begin)
        event.add('dtend', self.end)
        event.add('description', self.description)
        event.add('location', self.location)
        event.add('url', self.url)
        return event


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
                _calendar = Calendar()
                _calendar.calendar_name = calendar['name']
                _calendar.description = calendar.get('description', '')
                _calendar.add('prodid', '-//Sharks Ice Unofficial Calendar//EN')
                _calendar.add('version', '2.0')
                #_calendar.add('X-WR-CALNAME', calendar['name'])
                _calendar.add('X-WR-TIMEZONE', 'America/Los_Angeles')
                partition_keys = calendar.get("keys", [])
                
                logger.info(f"Generating calendar for {calendar['name']} with keys: {partition_keys}")
                
                events: Set[CalendarEvent] = set()
                
                # Query events from SQLite
                rows = get_events_by_partition(partition_keys)
                logger.info(f"Found {len(rows)} events for {calendar['name']}")
                
                for row in rows:
                    logger.info(f"Adding event {row.get('product_name')} on {row.get('start_date')}")
                    start_date = row.get("start_date")
                    end_date = row.get("end_date")
                    
                    # Parse date strings to datetime objects
                    if isinstance(start_date, str):
                        start_date = dateutil_parser.parse(start_date)
                    if isinstance(end_date, str):
                        end_date = dateutil_parser.parse(end_date)
                    
                    events.add(CalendarEvent(
                        name=row.get("product_name", ""),
                        begin=start_date,
                        end=end_date,
                        description=row.get("description", ""),
                        location=row.get("address", ""),
                        url="https://apps.daysmartrecreation.com/dash/x/#/online/sharks/event-registration"
                    ))
                
                for event in events:
                    _calendar.add_component(event.to_icalendar_event())
                
                # Save calendar to file
                calendar_path = CALENDARS_DIR / f"{calendar['name']}.ics"
                calendar_path.write_bytes(_calendar.to_ical())
                
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
