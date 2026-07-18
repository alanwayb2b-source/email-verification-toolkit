# Email Verification Toolkit

An open-source Python toolkit for cleaning, normalizing, deduplicating, and performing basic format validation on email addresses in CSV datasets.

## Features

- Clean and normalize email addresses
- Convert emails to lowercase
- Remove leading and trailing spaces
- Remove duplicate email records
- Check basic email syntax and format
- Add an `email_status` column
- Process CSV files
- No external Python packages required

## Important Note

This toolkit performs **format and syntax validation only**.

It does not connect to mail servers or verify whether a mailbox actually exists, is deliverable, or can receive email.

## Requirements

- Python 3.x

No additional Python libraries are required.

## Usage

Your input CSV file must contain a column named:

`email`

Example input:

| name | company | email |
|---|---|---|
| John Doe | Example Inc | JOHN@EXAMPLE.COM |
| Jane Smith | Demo Corp | jane@example.com |
| John Doe | Example Inc | john@example.com |

Run the tool from your terminal:

```bash
python email_cleaner.py input.csv output.csv
