# Horse Racing Scraper

This Python script scrapes horse racing information from Punters.com.au form guides.

## Setup

1. Install Python 3.7 or higher
2. Install required packages:
```
pip install -r requirements.txt
```

## Usage

Run the scraper:
```
python scraper.py
```

The script will:
1. Fetch data from the specified race URL
2. Extract all available text information
3. Save the data in a JSON file with timestamp
4. Print status messages during execution

## Output

The script creates a JSON file with the following information:
- Race name
- Race details
- List of horses and their information

The output file will be named `race_data_YYYYMMDD_HHMMSS.json`
