# Sharks Ice Unofficial Calendar

An unofficial calendar project that scrapes Sharks Ice ice rink events and makes them easily accessible.

## The Problem

Sharks Ice (operated by DaySmartRecreation) manages ice rinks across the Bay Area, but they don't provide:
- A dedicated mobile app
- An easy-to-use calendar interface
- Searchable event listings

## The Solution

This project leverages DaySmartRecreation's open API to scrape all available events and organize them into convenient calendar formats (iCalendar .ics files) that you can import into your preferred calendar application.

## Available Calendars

Currently, the project generates three ice hockey-focused calendars:

- **AllHockey** - All drop-in hockey sessions and Gretzky Hour events at all Bay Area locations
- **AllOaklandHockey** - Drop-in hockey and Gretzky Hour events at Oakland Ice Center
- **AllSanJoseHockey** - Drop-in hockey and Gretzky Hour events at Sharks Ice San Jose

Each calendar is available as an `.ics` file in the `data/calendars/` directory.

### Subscribing on Mobile Devices

Due to limitations with mobile browsers, the recommended way to subscribe to calendars on Android and iOS is through a desktop browser:

1. **Open calendar.google.com on your desktop or laptop** (not your phone)
2. **Click the + next to "Other calendars"** and select **"From URL"**
3. **Paste the calendar URL** (copy from the website) and click **"Add calendar"**
4. **The calendar will automatically sync** to your Google Calendar app on your phone

The calendar will then appear in the Google Calendar mobile app after it syncs (usually within a few minutes).

### Creating Custom Calendars

You can create your own custom calendars by adding entries to `configs/calendars.json`:

1. **Find Event Types**: Visit the [Events Database Viewer](events.html) to browse all available events and find the `partition_key` values you're interested in
2. **Edit calendars.json**: Add a new calendar entry with:
   - `name`: Your calendar name (used for the .ics filename)
   - `description`: A description of what's in the calendar
   - `keys`: An array of `partition_key` values to include in this calendar

Example:
```json
{
    "keys": [
        "Hockey:OIC-Drop-inHockey:OaklandIceCenterOperatedbySharksIce",
        "Performance/Strength:SJ-StrengthClass:SharksIceatSanJose"
    ],
    "name": "CustomHockeyAndStrength",
    "description": "Oakland drop-in hockey combined with San Jose strength training"
}
```

3. **Generate Calendars**: Run `python -m sharksice` to generate the new calendar file
4. **Use Your Calendar**: Import the generated `.ics` file into your calendar app

## Upcoming Features

- **Google Calendar Integration** - Calendars will be synced to a Google Calendar stream for easy subscription

## Project Structure

```
sharksiceunofficialcalendar/
├── sharksice/           # Main package
│   ├── calendars.py     # Calendar generation logic
│   ├── events.py        # Event parsing and processing
│   ├── utils.py         # Utility functions
│   └── __main__.py      # Entry point
├── configs/
│   └── calendars.json   # Calendar definitions
├── data/
│   └── calendars/       # Generated .ics calendar files
└── requirements.txt     # Python dependencies
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python -m sharksice`

## Disclaimer

⚠️ **Vibe Coded with GitHub Copilot** - This project was developed informally and may not always be reliable. It's maintained on a best-effort basis. Use at your own risk!
4. Import the generated `.ics` files from `data/calendars/` into your calendar app

## Contributing

Contributions are welcome! Areas where you can help:

- Add support for new event types or locations
- Improve event parsing and data accuracy
- Implement Google Calendar integration
- Add features or fix bugs
- Improve documentation

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.