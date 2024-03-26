"""Telegram analysis tools"""

from .telgeo import process_telegram_data

# From https://github.com/thomasjjj/Telegram_Geolocation_Scraper/tree/master. 
# Edited to run as function within Evidence Analyser environment.

def geolocate_telegram(case = 'default_case', from_case = False, append_to_case = True):
    
    if case == 'default_case':
        case = get_default_case()
    
    while True:
        
        # Step 1: Prompt for evidence data dictionary if required
        input_dict = None
        
        if from_case == True:
            
            item_id = input('ID of evidence to process: ')
            df = case['evidence'][item_id]['data']
            row_indexes = df[(df['Datatype'] == 'telegram_channel') | (df['Datatype'] == 'telegram')].index
            
            if len(row_indexes) == 0:
                raise ValueError(
                    'item must have data labelled with the datatypes: "telegram" or "telegram channel"'
                    )
                
            first_row_index = row_indexes.values[0]
            
            if df.loc[first_row_index, 'Stored as'] == dict:
                input_dict = df.loc[first_row_index, 'Raw data']
            
            else:
                raise TypeError('Telegram data must be stored as a dictionary')
        
        else: 
            from_file = True
        
        
        # Step 2: Prompt for CSV file name to save to if required
        
        if append_to_case == False:
        
            csv_file_name = input("Save file as: ")

        
        # Step 3: Prompt for file path to save to if required
        
        if append_to_case == False:
            csv_save_path = input(
                f"Save CSV file to: ")

            csv_save_path = csv_save_path + '.csv'

        # Step 4: Process the Data
        post_link_base = input("URL for post links (e.g., https://t.me/WarArchive_ua/): ")
        df = process_telegram_data(
                                                                post_link_base = post_link_base, 
                                                                from_file = from_file, 
                                                                input_dict = input_dict
                                                            )

        # Step 5: Save to CSV
        
        
        df.to_csv(csv_save_path, index=False, encoding='utf-8')
        print(f"CSV file saved as {csv_save_path}")
        
       

        # Step 6: Repeat or exit
        another_file = input("Do you want to process another dataset? (yes/no): ").strip().lower()
        if another_file != 'yes':
            break
            