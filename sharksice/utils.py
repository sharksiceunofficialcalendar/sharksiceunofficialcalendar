import logging
from datetime import datetime, timedelta
import pprint
import json
import re

import arrow

# Recursively search for all 'type' values in a nested structure
def collect_types(obj, types_set):
    """Recursively search for all 'type' values in a nested structure."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 'type':
                types_set.add(v)
            collect_types(v, types_set)
    elif isinstance(obj, list):
        for item in obj:
            collect_types(item, types_set)

# Only collect top-level objects in 'data' and 'included'
def collect_top_level_objects_by_type(obj_list, type_dicts):
    """Only collect top-level objects in 'data' and 'included'."""
    if isinstance(obj_list, list):
        for obj in obj_list:
            if isinstance(obj, dict) and 'type' in obj and 'id' in obj:
                t = obj['type']
                i = obj['id']
                if t not in type_dicts:
                    type_dicts[t] = {}
                type_dicts[t][i] = obj

def remove_empty_lists(obj):
    """Remove empty lists from nested objects."""
    if isinstance(obj, dict):
        return {k: remove_empty_lists(v) for k, v in obj.items() if not (isinstance(v, list) and len(v) == 0)}
    elif isinstance(obj, list):
        return [remove_empty_lists(item) for item in obj]
    else:
        return obj

def resolve_relationships(obj, type_dicts):
    """Resolve and embed relationships in objects."""
    if isinstance(obj, dict):
        if 'relationships' in obj:
            relationships = obj.pop('relationships')
            for rel_key, rel_val in relationships.items():
                if isinstance(rel_val, dict) and 'data' in rel_val:
                    rel_data = rel_val['data']
                    if isinstance(rel_data, dict):
                        rel_type = rel_data.get('type')
                        rel_id = rel_data.get('id')
                        if rel_type and rel_id and rel_type in type_dicts and rel_id in type_dicts[rel_type]:
                            obj['attributes'][rel_key] = resolve_relationships(type_dicts[rel_type][rel_id], type_dicts)
                    elif isinstance(rel_data, list):
                        resolved_list = []
                        for item in rel_data:
                            rel_type = item.get('type')
                            rel_id = item.get('id')
                            if rel_type and rel_id and rel_type in type_dicts and rel_id in type_dicts[rel_type]:
                                resolved_list.append(resolve_relationships(type_dicts[rel_type][rel_id], type_dicts))
                        obj['attributes'][rel_key] = resolved_list
                elif isinstance(rel_val, dict):
                    rel_type = rel_val.get('type')
                    rel_id = rel_val.get('id')
                    if rel_type and rel_id and rel_type in type_dicts and rel_id in type_dicts[rel_type]:
                        obj['attributes'][rel_key] = resolve_relationships(type_dicts[rel_type][rel_id], type_dicts)
                elif isinstance(rel_val, list):
                    resolved_list = []
                    for item in rel_val:
                        if isinstance(item, dict):
                            rel_type = item.get('type')
                            rel_id = item.get('id')
                            if rel_type and rel_id and rel_type in type_dicts and rel_id in type_dicts[rel_type]:
                                resolved_list.append(resolve_relationships(type_dicts[rel_type][rel_id], type_dicts))
                    obj['attributes'][rel_key] = resolved_list
        if 'attributes' in obj:
            obj['attributes'] = resolve_relationships(obj['attributes'], type_dicts)
        return obj
    elif isinstance(obj, list):
        return [resolve_relationships(item, type_dicts) for item in obj]
    else:
        return obj

def clean_obj(obj):
    """Clean object by removing unwanted keys and merging attributes."""
    deletable_keys = [
        # ...existing code...
        "standings_type", "hide_private_teams", "event_selection", "event_selection_weekly", "prorating", "max_teams", "display_standings", "is_flat_fee", "image_url", "free_trial", "default_registration_option", "is_makeups_enabled", "member_app_cost_display_mode", "best_image_url", "best_is_makeups_enabled", "team_type", "high_privacy", "is_free_trial_enabled", "enable_team_export", "is_makeups_enabled", "best_is_makeups_enabled", "sex", "min_birthdate", "max_birthdate", "standings_type", "min_age", "min_age_months", "max_age", "max_age_months", "allow_end_user_cancel", "hide_quantity", "non_resident_price", "hide_membership_online", "actual_price", "local_price", "has_location_pricing", "icon_defaulted", "image_url_default", "stat_table", "billing_type", "old_team_type_code", "code", "color", "event_type", "publish", "balance", "event_not_invoiced", "customer_balance", "customer_not_invoiced", "booking_balance", "has_balance", "free_trial_count", "comment_count", "free_trial_days_before", "free_trial_hours_before", "remaining_free_trial_slots", "has_invoicing", "has_roster", "has_home_team", "has_away_team", "allows_drop_ins", "allows_makeups", "makeups_max_per_event", "makeups_above_roster_limit", "makeups_count", "makeups_remaining_slots", "composite_capacity", "create_u", "created_user_type", "mod_u", "last_modified_user_type", "is_overtime", "has_gender_locker_rooms", "includes_setup_time", "includes_takedown_time", "private", "free_trial_opt_out", "has_free_trials", "best_free_trial_hours_before", "team_registered_count", "attendance_count", "remaining_roster_slots"
    ]
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k in ['id', 'links', 'type', 'eventType', 'comments', "event-comments"] or k.endswith('_id') or v is None or v == "" or k in deletable_keys:
                continue
            if k == 'attributes' and isinstance(v, dict):
                cleaned.update(clean_obj(v))
            else:
                cleaned[k] = clean_obj(v)
        return cleaned
    elif isinstance(obj, list):
        return [clean_obj(item) for item in obj]
    else:
        return obj
    
def remove_tags(text):
    """Remove HTML tags from text."""
    return re.sub(r'<.*?>', '', text)

def remove_escaped_characters(text):
    return re.sub(r'&.*?;', '', text)

def build_event_table(master):
    """Build a list of event dictionaries for output."""
    event_table = []
    events = master.get('events', {})
    for event_id, event in events.items():
        product = event.get('homeTeam', {}).get('product', {})
        sport = event.get('homeTeam', {}).get('sport', {})
        program_type = event.get('homeTeam', {}).get('programType', {})
        summary = event.get('summary', {})
        summary_name = summary.get("name")
        resource = event.get('resource', {})
        description = event.get('best_description', "")
        if not description:
            description = summary.get('description', "") or summary.get('best_description', "")
        program_type_name = program_type.get('name', summary_name)
        sport = sport.get('name', summary_name)
        product_name = product.get('name', summary_name)
        if program_type is None or sport is None or product_name is None:
            logging.warning(f"Missing data {event_id}\n{pprint.pprint(json.dumps(event, indent=4))}")
            continue
        row = {
            'EventID': event_id,
            'ProductName': product_name,
            'Sport': sport,
            'ProgramType': program_type_name,
            'PeopleRegistered': summary.get('registered_count'),
            'OpenSlots': summary.get('open_slots'),
            'Description': remove_escaped_characters(remove_tags(description)),
            'Facility': resource.get('facility', {}).get('name'),
            'Address': resource.get('facility', {}).get('address', {}).get('single_line_address'),
            'Resource': resource.get('name'),
            'StartDate': arrow.get(summary.get('start_date')).to('utc').datetime,
            'StartDateLocal': arrow.get(summary.get('start_date')).to('US/Pacific').format(arrow.FORMAT_RFC3339),
            'EndDate': arrow.get(summary.get('end_date')).to('utc').datetime,
            'EndDateLocal': arrow.get(summary.get('end_date')).to('US/Pacific').format(arrow.FORMAT_RFC3339),
            'IsRegistrationOpen': event.get('homeTeam', {}).get('is_registration_open'),
        }
        event_table.append(row)
    return event_table

def get_date_range(days):
    """Get start and end date for a range of days from today."""
    today = datetime.now()
    start_date = today
    end_date = today + timedelta(days=days)
    return start_date, end_date


def format_date_for_api(dt):
    """Format date for API query."""
    return dt.strftime("%Y-%m-%d")


def format_date_for_filename(dt):
    """Format date for filenames."""
    return f"{dt.month}_{dt.day}_{dt.year}"

def collect_events(data):
    """Collect and process events from API response."""
    type_dicts = {}
    for key in ['data', 'included']:
        if key in data:
            collect_top_level_objects_by_type(data[key], type_dicts)

    for t in type_dicts:
        for i in type_dicts[t]:
            type_dicts[t][i] = remove_empty_lists(type_dicts[t][i])

    master = {
        t: {
            i: clean_obj(resolve_relationships(obj, type_dicts))
            for i, obj in type_dicts[t].items()
        }
        for t in type_dicts
    }
    return build_event_table(master)
