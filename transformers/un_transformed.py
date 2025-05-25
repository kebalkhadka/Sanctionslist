import pandas as pd
import re
import os

# Function to clean normal text
def clean_text(text):
    if pd.isna(text):
        return ""
    cleaned = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
    return cleaned.strip()

# Function to detect non-ASCII garbage characters
def contains_garbage(text):
    try:
        text.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True

def clean_un_data():
    # Get absolute paths based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    input_csv = os.path.join(base_dir, 'output', 'un_UN_parsed.csv')
    output_csv = os.path.join(base_dir, 'cleaned', 'un_UN_cleaned.csv')

    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        return

    # Read CSV with correct encoding
    df = pd.read_csv(input_csv, encoding='latin1')  # or 'utf-8' with errors='replace'

    # Drop rows where 'Name' or 'Nationality' contains garbage characters
    df = df[~df['Name'].apply(contains_garbage)]
    df = df[~df['Nationality'].apply(lambda x: contains_garbage(str(x)))]

    # Clean columns
    df['Name'] = df['Name'].apply(clean_text)
    df['Alias'] = df['Alias'].apply(lambda x: None if contains_garbage(str(x)) else clean_text(x))
    df['Nationality'] = df['Nationality'].apply(clean_text)
    df['Sanction Type'] = df['Sanction Type'].apply(clean_text)
    df['Designation'] = df['Designation'].apply(clean_text)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save cleaned data
    df.to_csv(output_csv, index=False)
    print(f"✅ Cleaned UN data saved to: {output_csv}")

if __name__ == "__main__":
    clean_un_data()
