import requests
import csv
import time
import pandas as pd
from tqdm import tqdm
import os

def get_harvard_art_collection(api_key, max_objects=75000):
    """
    Fetch European and American Art collections from Harvard Art Museums API
    Using the specific key "European and American Art" for filtering
    """
    base_url = "https://api.harvardartmuseums.org/object"
    all_objects = []
    page = 1
    page_size = 100  # Harvard API allows up to 100 objects per request
    total_objects = 0
    
    print("Fetching European and American Art collections from Harvard Art Museums API...")
    
    # Using the specific key "European and American Art" as requested
    params = {
        'apikey': api_key,
        'size': page_size,
        'page': page,
        'division': 'European and American Art',  # Using the exact key specified
        'sort': 'rank',
        'sortorder': 'desc',
        'fields': 'id,objectnumber,title,people,dated,datebegin,dateend,period,culture,technique,medium,dimensions,provenance,department,division,creditline,classification,gallery,century,style,url,primaryimageurl,colors,images,imagepermissionlevel'
    }
    
    while True:
        params['page'] = page
        
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'records' in data and data['records']:
                objects_count = len(data['records'])
                all_objects.extend(data['records'])
                total_objects += objects_count
                
                print(f"Fetched page {page}, added {objects_count} objects. Total: {total_objects}")
                
                # Stop if we've collected enough objects or reached the end
                if total_objects >= max_objects:
                    print(f"Reached target of {max_objects} objects. Stopping data collection.")
                    all_objects = all_objects[:max_objects]  # Trim to max_objects
                    break
                    
                # Check if there are more pages
                if 'info' in data and total_objects < data['info']['totalrecords'] and total_objects < max_objects:
                    page += 1
                    time.sleep(0.5)  # Be nice to the API with a small delay
                else:
                    print("Reached end of collection data.")
                    break
            else:
                print("No more data available or empty response.")
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            break
    
    print(f"Fetched a total of {len(all_objects)} objects")
    return all_objects

def process_object_data(objects):
    """
    Process the raw object data to make it more CSV-friendly
    """
    processed_objects = []
    
    for obj in objects:
        processed_obj = {}
        
        # Copy basic fields
        for field in ['id', 'objectnumber', 'title', 'dated', 'datebegin', 'dateend', 
                     'period', 'culture', 'medium', 'technique', 'dimensions', 
                     'provenance', 'department', 'division', 'creditline', 
                     'classification', 'gallery', 'century', 'style', 'url', 'primaryimageurl']:
            processed_obj[field] = obj.get(field, '')
        
        # Process people/artists
        if 'people' in obj and obj['people']:
            artists = []
            roles = []
            for person in obj['people']:
                name = person.get('name', '')
                role = person.get('role', '')
                display_date = person.get('displaydate', '')
                
                if name:
                    artists.append(name)
                    if role and display_date:
                        roles.append(f"{name} ({role}, {display_date})")
                    elif role:
                        roles.append(f"{name} ({role})")
                    else:
                        roles.append(name)
            
            processed_obj['artists'] = '; '.join(artists)
            processed_obj['artistsroles'] = '; '.join(roles)
        else:
            processed_obj['artists'] = ''
            processed_obj['artistsroles'] = ''
        
        # Process colors
        if 'colors' in obj and obj['colors']:
            color_data = []
            for color in obj['colors']:
                hex_value = color.get('color', '')
                percent = color.get('percent', '')
                if hex_value and percent:
                    color_data.append(f"{hex_value} ({percent}%)")
            processed_obj['colors'] = '; '.join(color_data)
        else:
            processed_obj['colors'] = ''
        
        # Process image URLs
        if 'images' in obj and obj['images']:
            base_urls = []
            for image in obj['images']:
                base_url = image.get('baseimageurl', '')
                if base_url:
                    base_urls.append(base_url)
            processed_obj['additional_images'] = '; '.join(base_urls)
        else:
            processed_obj['additional_images'] = ''
            
        # Add image permission level
        processed_obj['imagepermissionlevel'] = obj.get('imagepermissionlevel', '')
            
        processed_objects.append(processed_obj)
    
    return processed_objects

def save_to_csv(objects, filename="harvard_european_american_art.csv"):
    """
    Save the processed collection data to a CSV file
    """
    if not objects:
        print("No data to save.")
        return
    
    # Define all the fields we want to save
    fieldnames = [
        'id', 'objectnumber', 'title', 'artists', 'artistsroles', 'dated', 
        'datebegin', 'dateend', 'century', 'period', 'culture', 
        'medium', 'technique', 'dimensions', 'provenance',
        'creditline', 'classification', 'department', 'division',
        'gallery', 'style', 'colors', 'url', 'primaryimageurl', 
        'additional_images', 'imagepermissionlevel'
    ]
    
    print(f"Saving data to {filename}...")
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for obj in tqdm(objects):
                # Fixed the name error: This creates a row dictionary with only the fields we want
                row_data = {}
                for field in fieldnames:
                    row_data[field] = obj.get(field, '')
                writer.writerow(row_data)
        
        print(f"Successfully saved {len(objects)} objects to {filename}")
        
        # Also save as Excel for convenience
        excel_filename = filename.replace('.csv', '.xlsx')
        df = pd.DataFrame(objects)
        # Only include the columns we defined
        df = df.reindex(columns=fieldnames)
        df.to_excel(excel_filename, index=False)
        print(f"Also saved data to Excel file: {excel_filename}")
        
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def verify_division_exists(api_key, division_name):
    """
    Verify that the specified division exists in the API
    """
    url = "https://api.harvardartmuseums.org/division"
    params = {'apikey': api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if 'records' in data:
            divisions = [div['name'] for div in data['records']]
            if division_name in divisions:
                print(f"✓ Confirmed: Division '{division_name}' exists")
                return True
            else:
                print(f"⚠ Warning: Division '{division_name}' not found")
                print("Available divisions:")
                for div in data['records']:
                    print(f"- {div['name']}")
                return False
    except Exception as e:
        print(f"Error verifying division: {e}")
        return False

def main():
    # Get API key from environment or prompt user
    api_key = os.environ.get("HARVARD_API_KEY")
    if not api_key:
        api_key = input("Enter your Harvard Art Museums API key: ")
    
    # Division name to use for filtering
    division_name = "European and American Art"
    
    # Verify the division exists
    verify_division_exists(api_key, division_name)
    
    # Get the data
    collection_data = get_harvard_art_collection(api_key, max_objects=75000)
    
    # Process the data
    if collection_data:
        processed_data = process_object_data(collection_data)
        
        # Save to CSV
        save_to_csv(processed_data)

if __name__ == "__main__":
    main()