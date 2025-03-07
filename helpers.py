import pandas as pd
import os
from typing import List

def find_column(dataframe, column_name):
  matching_columns = [col for col in dataframe.columns if col.lower() == column_name.lower()]
  return matching_columns[0] if matching_columns else None

def get_tag_value(row, dataframe, column_name):
  matching_column = find_column(dataframe, column_name)
  return row[matching_column] if matching_column and pd.notna(row[matching_column]) else '(not tagged)'

def process_aws_tags(input_file: str, output_file: str):
    """
    Process an AWS tags CSV file, extracting the desired columns and saving the result to a new CSV file.
    """
    # Columns to check for tag values
    tag_columns_to_check = [
        'Tag: Name', 
        'Tag: Env', 
        'Tag: Purpose', 
        'Tag: Owner', 
        'Tag: EOP', 
        'Tag: Contact'
    ]

    # Columns to keep in the output CSV
    desired_columns = [
        'Identifier', 'Service', 'Type', 'Region', 
        'Tag: Name', 'Tag: Env', 'Tag: Purpose', 
        'Tag: Owner', 'Tag: EOP', 'Tag: Contact', 
        'Tags', 'ARN'
    ]

    df = pd.read_csv(input_file)
    processed_df = pd.DataFrame(columns=desired_columns)

    for _, row in df.iterrows():
        new_row = {}
        tag_values = {}
        for col in tag_columns_to_check:
            tag_values[col] = get_tag_value(row, df, col)
        
        tagged_count = sum(1 for value in tag_values.values() if value != '(not tagged)')
        
        for col in tag_columns_to_check:
            new_row[col] = tag_values[col]
        

        for col in desired_columns:
            if col not in tag_columns_to_check:
                if col == 'Tags':
                    new_row[col] = tagged_count
                else:
                    matched_column = find_column(df, col)
                    if matched_column:
                        new_row[col] = row[matched_column] if pd.notna(row[matched_column]) else '(not tagged)'
                    else:
                        new_row[col] = '(not tagged)'
        
        new_row_df = pd.DataFrame([new_row])
        processed_df = pd.concat([processed_df, new_row_df], ignore_index=True)

    # Save Csv
    processed_df.to_csv(output_file, index=False)
    print(f"Processed CSV saved to {output_file}")
    print(f"Total records processed: {len(processed_df)}")

    return output_file

# #Test the function
# def main():

#   input_file = 'tags_services_account/carlos.posada@techgenies.com_all_20250303.csv'
#   output_file = 'tags_services_account/processed_aws_tags_3.csv'
#   process_aws_tags(input_file, output_file)

# if __name__ == "__main__":
#     main()