import json
import csv
from datetime import datetime

def process_runner_details():
    # Read the JSON file
    with open('race_data_20241216_135755.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Prepare CSV data
    csv_data = []
    headers = ['Number', 'Horse Name', 'Barrier', 'Jockey', 'Weight', 'Trainer', 'Last 10', 'Career', 'Rating', 'Win %', 'Place %', 'Avg Prize', 'Odds', 'Open', 'Flucs Percentage']
    
    # Process each horse entry
    for horse in data['horse_information']:
        horse_data = {}
        
        # Extract relevant information
        horse_data['Number'] = horse.get('Number', '-')
        horse_data['Horse Name'] = horse.get('Horse Name', '-')
        horse_data['Barrier'] = horse.get('Barrier', '-')
        horse_data['Jockey'] = horse.get('Jockey', '-')
        horse_data['Weight'] = horse.get('Weight', '-')
        horse_data['Trainer'] = horse.get('Trainer', '-')
        horse_data['Last 10'] = horse.get('Last 10', '-')
        horse_data['Career'] = horse.get('Career', '-')
        horse_data['Rating'] = horse.get('Rating', '-')
        horse_data['Win %'] = horse.get('Win %', '-')
        horse_data['Place %'] = horse.get('Place %', '-')
        horse_data['Avg Prize'] = horse.get('Avg Prize $', '-')
        horse_data['Odds'] = horse.get('Odds', '-')
        horse_data['Open'] = horse.get('Open', '-')
        horse_data['Flucs Percentage'] = horse.get('flucs_percentage', '-')
        
        # Add to CSV data
        csv_data.append([horse_data[header] for header in headers])
    
    # Write to CSV file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'runner_details_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(csv_data)

if __name__ == "__main__":
    process_runner_details()