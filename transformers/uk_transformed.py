# import pandas as pd
# import re
# import os

# def clean_text(text):
#     if pd.isna(text):
#         return ""
#     text = re.sub(r'[^\w\s]', '', str(text))  # Remove special characters
#     text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single
#     return text.strip()

# def clean_uk_data(input_csv='../output/uk_uk_parsed.csv', output_csv='../cleaned/uk_sanctions_cleaned.csv'):
#     # Load the CSV
#     df = pd.read_csv(input_csv, encoding='latin1')

#     # Clean each relevant column
#     df['Name'] = df['Name'].apply(clean_text)
#     df['Alias'] = df['Alias'].apply(lambda x: None if pd.isna(x) else clean_text(x))
#     df['Nationality'] = df['Nationality'].apply(clean_text)
#     df['Sanction Type'] = df['Sanction Type'].apply(clean_text)
#     df['Designation'] = df['Designation'].apply(clean_text)

#     # Remove duplicate names with same nationality, keeping one with a designation
#     df.sort_values(by='Designation', ascending=False, inplace=True)
#     df = df.drop_duplicates(subset=['Name', 'Nationality'], keep='first')

#     # Save cleaned version
#     os.makedirs(os.path.dirname(output_csv), exist_ok=True)
#     df.to_csv(output_csv, index=False)
#     print(f"✅ Cleaned UK sanctions data saved to: {output_csv}")

# if __name__ == "__main__":
#     clean_uk_data()
import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Resolve paths relative to this script's folder
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # Assuming 'transformers' is one folder under root

input_csv = os.path.join(project_root, 'output', 'uk_uk_parsed.csv')
output_csv = os.path.join(project_root, 'cleaned', 'uk_sanctions_cleaned.csv')

df = pd.read_csv(input_csv)

def fill_missing_designations(df):
    # Your existing function code unchanged
    known_df = df[df['Designation'].notnull()]
    class_counts = known_df['Designation'].value_counts()
    valid_classes = class_counts[class_counts >= 2].index
    filtered_df = known_df[known_df['Designation'].isin(valid_classes)].copy()

    missing_df = df[df['Designation'].isnull()].copy()

    if len(filtered_df) == 0 or len(missing_df) == 0:
        print("❌ Not enough data to fill missing designations.")
        return df

    filtered_df['input_text'] = filtered_df['Name'].fillna('') + ' ' + filtered_df['Nationality'].fillna('')
    missing_df['input_text'] = missing_df['Name'].fillna('') + ' ' + missing_df['Nationality'].fillna('')

    vectorizer = TfidfVectorizer(max_features=1000)
    X_train_vec = vectorizer.fit_transform(filtered_df['input_text'])
    X_missing_vec = vectorizer.transform(missing_df['input_text'])

    clf = LogisticRegression(max_iter=1000)
    clf.fit(X_train_vec, filtered_df['Designation'])

    missing_predictions = clf.predict(X_missing_vec)
    df.loc[missing_df.index, 'Designation'] = missing_predictions
    print(f"✅ Filled {len(missing_predictions)} missing designations.")
    return df

df = fill_missing_designations(df)
os.makedirs(os.path.dirname(output_csv), exist_ok=True)  # Make sure folder exists
df.to_csv(output_csv, index=False)
print(f"✅ Cleaned UK sanctions saved to: {output_csv}")
