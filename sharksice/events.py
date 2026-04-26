#!/usr/bin/env python3
"""
Standalone script to fetch events from the API and store them in SQLite.
"""

import logging
import re
import asyncio
import sqlite3
import json
import pathlib
from datetime import datetime
from typing import List, Dict, Any

import httpx

from .utils import get_date_range, format_date_for_api, collect_events

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

DB_PATH = pathlib.Path(__file__).parent.parent / "events.db"


def init_database():
    """Initialize SQLite database with events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            partition_key TEXT NOT NULL,
            row_key TEXT NOT NULL,
            product_name TEXT,
            sport TEXT,
            program_type TEXT,
            description TEXT,
            facility TEXT,
            address TEXT,
            start_date TIMESTAMP,
            start_date_local TEXT,
            end_date TIMESTAMP,
            end_date_local TEXT,
            people_registered INTEGER,
            open_slots INTEGER,
            resource TEXT,
            is_registration_open BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def upsert_events(events: List[Dict[str, Any]]) -> bool:
    """Insert or update events in SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for event in events:
            cursor.execute('''
                INSERT OR REPLACE INTO events (
                    id, partition_key, row_key, product_name, sport, program_type,
                    description, facility, address, start_date, start_date_local,
                    end_date, end_date_local, people_registered, open_slots,
                    resource, is_registration_open, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event['RowKey'],
                event['PartitionKey'],
                event['RowKey'],
                event.get('ProductName'),
                event.get('Sport'),
                event.get('ProgramType'),
                event.get('Description'),
                event.get('Facility'),
                event.get('Address'),
                event.get('StartDate'),
                event.get('StartDateLocal'),
                event.get('EndDate'),
                event.get('EndDateLocal'),
                event.get('PeopleRegistered'),
                event.get('OpenSlots'),
                event.get('Resource'),
                event.get('IsRegistrationOpen'),
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error upserting events: {e}", exc_info=True)
        return False


async def fetch_and_store_events():
    """Fetch events from the API and store them in SQLite."""
    try:
        init_database()
        
        start, end = get_date_range(7)
        start_str = format_date_for_api(start)
        end_str = format_date_for_api(end)
        
        url = "https://apps.daysmartrecreation.com/dash/jsonapi/api/v1/events"
        querystring = {
            "sort": "end,start",
            "include": "summary,comments,resource.facility.address,resource.address,eventType.product.locations,homeTeam.facility.address,homeTeam.league.season.priorities.memberships,homeTeam.league.season.priorities.activatedBySeasons,homeTeam.programType,homeTeam.product,homeTeam.product.locations,homeTeam.sport",
            "filter[start_date__gte]": start_str,
            "filter[start_date__lte]": end_str,
            "page[size]": 50,
            "filter[unconstrained]": "1",
            "filterRelations[comments.comment_type]": "public",
            "company": "sharks",
        }
        
        logger.info(f"Fetching events from {start_str} to {end_str}")
        
        raw_events = []
        current_page = 1
        last_page = 1
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=querystring)
            
            if resp.status_code != 200:
                logger.error(f"Error fetching events: {resp.status_code}")
                return False
            
            data = resp.json()
            logger.info(f"Fetched page 1 of events.")
            raw_events.extend(data.get("data", []))
            
            metadata = data.get("meta", {}).get("page", {})
            current_page = metadata.get("current-page", 1)
            last_page = metadata.get("last-page", 1)
            
            # Process first page
            events_to_write = []
            for event in collect_events(data):
                pk = ":".join([
                    event['Sport'].replace(" ", ""),
                    event['ProductName'].replace(" ", ""),
                    event['Facility'].replace(" ", "")
                ])
                pk = re.sub(r"\(\d+Min\)|\(\d+\+\)|\(\dHour\)|\(\d+-\d+\)|@|\(\d+Minutes\)|\(\w+-\w+\)|\d-hr|\d+-\d+", "", pk, 0)
                event['PartitionKey'] = pk
                event['RowKey'] = event['EventID']
                event.pop("EventID")
                events_to_write.append(event)
            
            # Write first page to database
            if not upsert_events(events_to_write):
                return False
            logger.info(f"Stored {len(events_to_write)} events from page 1")
            
            # Fetch remaining pages
            while current_page < last_page:
                current_page += 1
                querystring["page[number]"] = current_page
                logger.info(f"Fetching page {current_page} of {last_page} events.")
                
                resp = await client.get(url, params=querystring)
                if resp.status_code != 200:
                    logger.error(f"Error fetching events: {resp.status_code}")
                    return False
                
                data = resp.json()
                raw_events.extend(data.get("data", []))
                
                # Process events from current page
                events_to_write = []
                for event in collect_events(data):
                    pk = ":".join([
                        event['Sport'].replace(" ", ""),
                        event['ProductName'].replace(" ", ""),
                        event['Facility'].replace(" ", "")
                    ])
                    pk = re.sub(r"\(\d+Min\)|\(\d+\+\)|\(\dHour\)|\(\d+-\d+\)|@|\(\d+Minutes\)|\(\w+-\w+\)|\d-hr|\d+-\d+", "", pk, 0)
                    event['PartitionKey'] = pk
                    event['RowKey'] = event['EventID']
                    event.pop("EventID")
                    events_to_write.append(event)
                
                # Write current page to database
                if not upsert_events(events_to_write):
                    return False
                logger.info(f"Stored {len(events_to_write)} events from page {current_page}")
                
                metadata = data.get("meta", {}).get("page", {})
                current_page = metadata.get("current-page", current_page)
                last_page = metadata.get("last-page", last_page)
        
        # Save raw events for reference
        pathlib.Path("raw_events.json").write_text(json.dumps(raw_events, indent=4))
        logger.info(f"Successfully fetched and stored {len(raw_events)} events")
        logger.info(f"Database file: {DB_PATH}")
        return True
        
    except Exception as e:
        logger.error(f"Error in fetch_and_store_events: {e}", exc_info=True)
        return False


async def main():
    """Main entry point."""
    success = await fetch_and_store_events()
    if not success:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
