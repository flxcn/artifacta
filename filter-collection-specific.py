import pandas as pd
import csv
import os
from tqdm import tqdm

def extract_belinda_records(input_csv="harvard_european_american_art.csv", 
                           output_csv="belinda_lull_randall_collection.csv"):
    """
    Extracts records containing 'Belinda Lull Randall' from the Harvard Art Museums CSV
    and saves them to a new CSV file.
    """
    print(f"Reading data from {input_csv}...")
    
    try:
        # Check if file exists
        if not os.path.exists(input_csv):
            print(f"Error: Input file '{input_csv}' not found.")
            return False
        
        # Read the CSV file
        df = pd.read_csv(input_csv)
        
        # Check if we have data
        if df.empty:
            print("Error: The input CSV file is empty.")
            return False
            
        print(f"Successfully loaded {len(df)} records from the CSV file.")
        
        # Filter rows containing "Belinda Lull Randall" in any column
        # First convert all columns to string to ensure we can search through them
        for col in df.columns:
            df[col] = df[col].astype(str)
            
        # Search for "Belinda Lull Randall" in any column
        belinda_df = df[df.apply(lambda row: row.astype(str).str.contains('Belinda Lull Randall', case=False).any(), axis=1)]
        
        # Check if we found any matches
        if belinda_df.empty:
            print("No records containing 'Belinda Lull Randall' were found.")
            return False
            
        print(f"Found {len(belinda_df)} records containing 'Belinda Lull Randall'.")
        
        # Save the filtered data to a new CSV file
        belinda_df.to_csv(output_csv, index=False)
        
        # Also save as Excel for convenience
        excel_filename = output_csv.replace('.csv', '.xlsx')
        belinda_df.to_excel(excel_filename, index=False)
        
        print(f"Successfully saved {len(belinda_df)} records to {output_csv}")
        print(f"Also saved data to Excel file: {excel_filename}")
        
        # Display a preview of the records found
        print("\nPreview of records containing 'Belinda Lull Randall':")
        preview_cols = ['objectnumber', 'title', 'artists', 'dated']
        available_cols = [col for col in preview_cols if col in belinda_df.columns]
        
        if available_cols:
            preview_df = belinda_df[available_cols]
            print(preview_df.head(5).to_string())
        
        return True
        
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return False

def search_specific_columns(input_csv="harvard_european_american_art.csv"):
    """
    Analyzes which columns contain 'Belinda Lull Randall' to help understand 
    her relationship to the collection.
    """
    try:
        # Check if file exists
        if not os.path.exists(input_csv):
            print(f"Error: Input file '{input_csv}' not found.")
            return
            
        # Read the CSV file
        df = pd.read_csv(input_csv)
        
        # Convert all columns to string
        for col in df.columns:
            df[col] = df[col].astype(str)
        
        print("\nSearching for 'Belinda Lull Randall' in specific columns:")
        
        # Check each column individually
        for col in df.columns:
            matches = df[df[col].str.contains('Belinda Lull Randall', case=False)]
            if not matches.empty:
                print(f"- Found {len(matches)} mentions in column '{col}'")
                
                # Show sample values for this column
                if len(matches) <= 5:
                    print("  Values:")
                    for val in matches[col].unique():
                        print(f"  - {val}")
                else:
                    print("  Sample values:")
                    for val in matches[col].unique()[:5]:
                        print(f"  - {val}")
        
    except Exception as e:
        print(f"Error analyzing columns: {e}")

def main():
    # Default filenames
    input_csv = "harvard_european_american_art.csv"
    output_csv = "belinda_lull_randall_collection.csv"
    
    # Check if the input file exists or prompt for a different filename
    if not os.path.exists(input_csv):
        input_csv = input(f"File '{input_csv}' not found. Please enter the correct CSV filename: ")
        if not os.path.exists(input_csv):
            print(f"Error: File '{input_csv}' not found. Exiting.")
            return
    
    # Extract records containing "Belinda Lull Randall"
    if extract_belinda_records(input_csv, output_csv):
        # Analyze which columns contain the name
        search_specific_columns(input_csv)

if __name__ == "__main__":
    main()