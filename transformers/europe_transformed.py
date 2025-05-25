import pandas as pd
import re
import os

# Fix mojibake 
def fix_mojibake(text):
    if pd.isna(text):
        return ""
    try:
        return text.encode('latin1').decode('utf-8')
    except Exception:
        return text

# Clean general text: remove punctuation, normalize spaces
def clean_text(text):
    if pd.isna(text):
        return ""
    cleaned = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalize whitespace
    return cleaned.strip()

# Detect non-ASCII (likely garbage)
def contains_garbage(text):
    try:
        text.encode('ascii')
        return False
    except UnicodeEncodeError:
        return True

# Simplify designation (only keep the first phrase/sentence)
def simplify_designation(text):
    if pd.isna(text):
        return ""
    simple = re.split(r'[.-]', text)[0]
    return clean_text(simple)

# Main cleaning function
def clean_europe_data():
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    input_csv = os.path.join(base_dir, 'output', 'eur_Europe_parsed.csv')
    output_csv = os.path.join(base_dir, 'cleaned', 'eur_Europe_cleaned.csv')

    # Check if file exists
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        return

    # Read with encoding (try utf-8 first, fallback to latin1)
    try:
        df = pd.read_csv(input_csv, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(input_csv, encoding='latin1')

    # Fix mojibake in relevant fields
    df['Name'] = df['Name'].apply(fix_mojibake)
    df['Alias'] = df['Alias'].apply(lambda x: fix_mojibake(str(x)) if not pd.isna(x) else "")

    # Drop rows with garbage in Name or Nationality
    df = df[~df['Name'].apply(contains_garbage)]
    df = df[~df['Nationality'].apply(lambda x: contains_garbage(str(x)))]

    # Apply text cleaning
    df['Name'] = df['Name'].apply(clean_text)
    def get_first_alias(alias_text):
        if pd.isna(alias_text) or contains_garbage(str(alias_text)):
            return None
        first_alias = re.split(r'[;,/]',alias_text)[0]
        return clean_text(first_alias)
    df['Alias'] = df['Alias'].apply(get_first_alias)
    df['Nationality'] = df['Nationality'].apply(clean_text)
    df['Sanction Type'] = df['Sanction Type'].apply(clean_text)
    df['Designation'] = df['Designation'].apply(simplify_designation)

    # Create output dir
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save cleaned data
    df.to_csv(output_csv, index=False)
    print(f"✅ Cleaned Europe data saved to: {output_csv}")

if __name__ == "__main__":
    clean_europe_data()
