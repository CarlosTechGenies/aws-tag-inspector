# AWS Tags Scanner

AWS Tags Scanner is a Python-based tool that automates the extraction and processing of AWS resource tags using Playwright for browser automation and Pandas for data manipulation. It allows users to export AWS tags from the Tag Editor and process them into structured CSV files.

## Features

- Automates AWS login and navigation to the Tag Editor.

- Supports MFA authentication.

- Extracts and processes AWS resource tags.

- Saves the processed tags into a CSV file for further analysis.

## Install dependencies

`pip install -r requirements.txt`

## Usage

Run the script to start the AWS tag extraction process:

`python tags_aws_account_2.0.py`

Follow the prompts to enter AWS credentials and navigate through the process.

## Future Updates

- Error Handling: Implement error handling for invalid credentials and incorrect MFA codes.

- Executable Version: Convert the script into a portable executable for easier distribution.

- Select Multiple Region:currently only allows scanning all regions or a single specific region.

## License

This project is licensed under the MIT License.
