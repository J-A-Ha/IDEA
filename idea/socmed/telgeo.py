# From https://github.com/thomasjjj/Telegram_Geolocation_Scraper/tree/master.
# Edited to improve functionality within Evidence Analyser environment.

import json
import pandas as pd
import re
from tkinter import filedialog
from tkinter import Tk


def process_telegram_data(post_link_base, from_file = True, input_dict = None):
    
    # Initialize an empty list to hold messages with coordinates
    messages_with_coordinates = []

    # Regular expression pattern to find latitude and longitude
    coordinate_pattern = re.compile(r'(-?\d+\.\d+),\s*(-?\d+\.\d+)')
    
    # Load the JSON file
    
    if from_file == True:
        
        json_file_path = input("JSON file to process: ")

        with open(json_file_path, 'r', encoding='utf-8') as f:
            telegram_data = json.load(f)
    
    else:
        telegram_data = input_dict

    # Iterate through all messages to find those with coordinates
    for message in telegram_data['messages']:
        text_field = str(message.get('text', ''))
        coordinates_match = coordinate_pattern.search(text_field)

        if coordinates_match:
            latitude, longitude = coordinates_match.groups()
            post_id = message.get('id', 'N/A')
            post_date = message.get('date', 'N/A')
            post_type = message.get('type', 'N/A')
            post_text = text_field
            media_type = message.get('media_type', 'N/A')

            message_info = {
                'Post ID': post_id,
                'Post Date': post_date,
                'Post Message': post_text,
                'Post Type': post_type,
                'Media Type': media_type,
                'Latitude': latitude,
                'Longitude': longitude
            }

            messages_with_coordinates.append(message_info)

    # Create a DataFrame and add the Post Link
    df = pd.DataFrame(messages_with_coordinates)
    df['Post Link'] = post_link_base + df['Post ID'].astype(str)

    # Reorder the columns
    column_order = ['Post Link', 'Post ID', 'Post Date', 'Post Message', 'Post Type', 'Media Type', 'Latitude',
                    'Longitude']
    df = df[column_order]

    return df

