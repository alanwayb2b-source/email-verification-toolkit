import csv
import re
import sys


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def clean_email(email):
    """Clean and normalize an email address."""
    if not email:
        return ""
    return email.strip().lower()


def is_valid_email(email):
    """Check whether an email has a valid basic format."""
    email = clean_email(email)
    return bool(EMAIL_PATTERN.match(email))


def process_csv(input_file, output_file):
    """
    Clean emails, remove duplicates, and add validation status.
    The input CSV must contain a column named 'email'.
    """
    seen_emails = set()

    with open(input_file, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames or "email" not in [
            name.lower() for name in reader.fieldnames
        ]:
            raise ValueError("Input CSV must contain an 'email' column.")

        email_column = next(
            name for name in reader.fieldnames if name.lower() == "email"
        )

        fieldnames = list(reader.fieldnames)
        if "email_status" not in fieldnames:
            fieldnames.append("email_status")

        with open(output_file, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                email = clean_email(row.get(email_column, ""))

                if not email or email in seen_emails:
                    continue

                seen_emails.add(email)
                row[email_column] = email
                row["email_status"] = (
                    "valid_format" if is_valid_email(email) else "invalid_format"
                )

                writer.writerow(row)

    print(f"Done! Cleaned file saved to: {output_file}")
    print(f"Unique email records processed: {len(seen_emails)}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python email_cleaner.py input.csv output.csv")
        sys.exit(1)

    process_csv(sys.argv[1], sys.argv[2])
