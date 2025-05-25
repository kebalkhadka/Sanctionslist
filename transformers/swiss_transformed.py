import pandas as pd
import os

def swiss_transformed():
    # Set base directory here manually since you have full paths
    base_dir = r'D:\BigData\Sanctions_etl'

    input_csv = os.path.join(base_dir, 'output', 'swiss_Swizerland_parsed.csv')
    output_csv = os.path.join(base_dir, 'cleaned', 'swiss_Swizerland_cleaned.csv')

    # Check if input file exists
    if not os.path.exists(input_csv):
        print(f"❌ Input file not found: {input_csv}")
        return

    # Read the parsed CSV (already cleaned)
    df = pd.read_csv(input_csv, encoding='utf-8')

    # Ensure the cleaned folder exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Save as cleaned CSV (no changes here, just copying with a new name)
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"✅ Saved cleaned file to: {output_csv}")

if __name__ == "__main__":
    swiss_transformed()
