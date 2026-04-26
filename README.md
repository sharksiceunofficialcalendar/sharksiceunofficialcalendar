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