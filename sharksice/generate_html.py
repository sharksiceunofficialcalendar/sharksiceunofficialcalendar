"""Generate index.html from calendars.json configuration."""

import json
import os
from pathlib import Path


def load_calendars_config(config_path="configs/calendars.json"):
    """Load calendars configuration from JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)


def generate_calendar_rows(calendars):
    """Generate HTML table rows for each calendar."""
    rows = []
    for calendar in calendars:
        name = calendar["name"]
        description = calendar["description"]
        
        # GitHub raw release URLs
        base_url = f"https://github.com/sharksiceunofficialcalendar/sharksiceunofficialcalendar/releases/latest/download/{name}.ics"
        webcal_url = f"webcal://github.com/sharksiceunofficialcalendar/sharksiceunofficialcalendar/releases/latest/download/{name}.ics"
        google_calendar_url = f"https://calendar.google.com/calendar/r?cid={webcal_url}"
        
        row = f"""                        <tr>
                            <td class="calendar-name">{name}</td>
                            <td class="calendar-desc">{description}</td>
                            <td>
                                <a href="{webcal_url}" class="download-btn">Subscribe *works with iOS*</a>
                                <a href="{google_calendar_url}" class="download-btn" style="background: #4CAF50;">Subscribe via Google Calendar</a>
                                <a href="{base_url}" class="download-btn" style="background: #764ba2;">Download</a>
                            </td>
                        </tr>"""
        rows.append(row)
    
    return "\n".join(rows)


def generate_index_html(calendars):
    """Generate the complete index.html content."""
    table_rows = generate_calendar_rows(calendars)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sharks Ice Unofficial Calendar</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 20px;
        }}

        .header img {{
            width: 120px;
            height: 120px;
            margin-bottom: 20px;
            filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
        }}

        .content {{
            padding: 40px 30px;
        }}

        .problem-section {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 25px;
            margin-bottom: 40px;
            border-radius: 4px;
            line-height: 1.6;
        }}

        .problem-section h2 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.4em;
        }}

        .problem-section p {{
            color: #555;
            font-size: 1.05em;
        }}

        .calendars-section h2 {{
            color: #333;
            margin-bottom: 25px;
            font-size: 1.4em;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}

        thead {{
            background: #f8f9fa;
            border-bottom: 2px solid #667eea;
        }}

        th {{
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        .calendar-name {{
            font-weight: 600;
            color: #333;
        }}

        .calendar-desc {{
            color: #666;
            font-size: 0.95em;
        }}

        .download-btn {{
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            text-decoration: none;
            font-size: 0.95em;
            font-weight: 500;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            margin-right: 8px;
        }}

        .download-btn:last-child {{
            margin-right: 0;
        }}

        .download-btn:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .footer {{
            text-align: center;
            color: #999;
            padding: 20px 30px;
            border-top: 1px solid #e9ecef;
            font-size: 0.9em;
        }}

        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 1.8em;
            }}

            .content {{
                padding: 20px 15px;
            }}

            table {{
                font-size: 0.9em;
            }}

            th, td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="img/shark.png" alt="Sharks Ice Logo">
            <h1>Sharks Ice Unofficial Calendar</h1>
        </div>

        <div class="content">
            <div class="problem-section">
                <h2>The Problem</h2>
                <p>Sharks Ice facilities use DASH by DaySmart as their scheduling system. DaySmart does not offer any type of official calendar export or calendar application. This project provides downloadable calendar files (.ics format) that you can import into your favorite calendar app (Google Calendar, Apple Calendar, Outlook, etc.) to stay updated on all events.</p>
            </div>

            <div class="calendars-section">
                <h2>Available Calendars</h2>
                <p style="margin-bottom: 25px; color: #666;">
                    <strong>Want to search events?</strong> Check out our <a href="events.html" style="color: #667eea; text-decoration: none; font-weight: 600;">Events Database Viewer</a> to browse and search all upcoming events.
                </p>
                <table>
                    <thead>
                        <tr>
                            <th>Calendar</th>
                            <th>Description</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
{table_rows}
                    </tbody>
                </table>

                <div style="background: #f0f7ff; border-left: 4px solid #667eea; padding: 20px; margin-bottom: 30px; margin-top: 30px; border-radius: 4px;">
                    <h3 style="color: #333; margin-bottom: 10px; font-size: 1.1em;">📱 Subscribing on Mobile (Android/iOS)</h3>
                    <p style="color: #555; margin-bottom: 15px;"><strong>Pro Tip:</strong> Mobile browsers have limitations with calendar subscriptions. Here's what actually works:</p>
                    <ol style="color: #555; line-height: 1.8;">
                        <li><strong>Open calendar.google.com on your desktop or laptop</strong> (not your phone)</li>
                        <li><strong>Click the + next to "Other calendars"</strong> and select <strong>"From URL"</strong></li>
                        <li><strong>Paste the calendar URL</strong> and click <strong>"Add calendar"</strong></li>
                        <li><strong>Your phone will sync automatically</strong> — the calendar appears in Google Calendar app within minutes</li>
                    </ol>
                </div>

                <div style="background: #f0f7ff; border-left: 4px solid #667eea; padding: 20px; margin-top: 30px; border-radius: 4px;">
                    <h3 style="color: #333; margin-bottom: 10px; font-size: 1.1em;">Create Your Own Calendar</h3>
                    <p style="color: #555; margin-bottom: 15px;">Want a custom calendar with only the events you care about?</p>
                    <ol style="color: #555; line-height: 1.8;">
                        <li>Visit the <a href="events.html" style="color: #667eea; font-weight: 600; text-decoration: none;">Events Database Viewer</a> and browse events</li>
                        <li>Note the <strong>Event Type</strong> (partition_key) values you want to include</li>
                        <li>Edit <code style="background: #fff; padding: 2px 6px; border-radius: 3px;">configs/calendars.json</code> and add a new calendar entry with those event types</li>
                        <li>Run <code style="background: #fff; padding: 2px 6px; border-radius: 3px;">python -m sharksice</code> to generate your calendar</li>
                        <li>Import the new .ics file into your calendar app</li>
                    </ol>
                    <p style="color: #555; margin-top: 15px; font-size: 0.9em;"><strong>See the <a href="README.md" style="color: #667eea; font-weight: 600; text-decoration: none;">README</a> for detailed instructions and examples.</strong></p>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>⚠️ <strong>Vibe Coded:</strong> This project is maintained informally and may not always be reliable. Use at your own risk.</p>
            <p style="margin-top: 10px; font-size: 0.85em;">Unofficial calendar maintained independently. For official Sharks Ice information, visit their website.</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content


def main():
    """Load config and generate index.html."""
    # Determine the root directory (parent of sharksice directory)
    root_dir = Path(__file__).parent.parent
    
    # Load calendars configuration
    config_path = root_dir / "configs" / "calendars.json"
    calendars = load_calendars_config(str(config_path))
    
    # Generate HTML
    html_content = generate_index_html(calendars)
    
    # Write to index.html
    output_path = root_dir / "index.html"
    with open(output_path, "w") as f:
        f.write(html_content)
    
    print(f"✓ Generated {output_path}")


if __name__ == "__main__":
    main()
