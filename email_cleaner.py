import csv
import re
import sys
from pathlib import Path


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def clean_email(email):
    """Clean and normalize an email address."""
    if not email:
        return ""
    return str(email).strip().lower()


def is_valid_email(email):
    """Check whether an email has a valid basic format."""
    email = clean_email(email)
    return bool(EMAIL_PATTERN.match(email))


def load_disposable_domains(filename="disposable_domains.txt"):
    """Load known disposable email domains from a text file."""
    path = Path(filename)

    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8") as file:
        return {
            line.strip().lower()
            for line in file
            if line.strip() and not line.startswith("#")
        }


def is_disposable_email(email, disposable_domains=None):
    """Check whether an email uses a known disposable email domain."""
    email = clean_email(email)

    if "@" not in email:
        return False

    if disposable_domains is None:
        disposable_domains = load_disposable_domains()

    domain = email.rsplit("@", 1)[1]

    return domain in disposable_domains


def process_csv(input_file, output_file, check_disposable=True):
    """
    Clean emails, remove duplicates, validate format,
    and optionally detect disposable email addresses.

    The input CSV must contain a column named 'email'.
    """
    seen_emails = set()

    disposable_domains = (
        load_disposable_domains()
        if check_disposable
        else set()
    )

    with open(input_file, "r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)

        if not reader.fieldnames or "email" not in [
            name.lower() for name in reader.fieldnames
        ]:
            raise ValueError("Input CSV must contain an 'email' column.")

        email_column = next(
            name for name in reader.fieldnames
            if name.lower() == "email"
        )

        fieldnames = list(reader.fieldnames)

        if "email_status" not in fieldnames:
            fieldnames.append("email_status")

        if "disposable_email" not in fieldnames:
            fieldnames.append("disposable_email")

        with open(
            output_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as outfile:

            writer = csv.DictWriter(
                outfile,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for row in reader:
                email = clean_email(
                    row.get(email_column, "")
                )

                if not email or email in seen_emails:
                    continue

                seen_emails.add(email)

                row[email_column] = email

                row["email_status"] = (
                    "valid_format"
                    if is_valid_email(email)
                    else "invalid_format"
                )

                if check_disposable:
                    row["disposable_email"] = (
                        "yes"
                        if is_disposable_email(
                            email,
                            disposable_domains
                        )
                        else "no"
                    )
                else:
                    row["disposable_email"] = "not_checked"

                writer.writerow(row)

    print(
        f"Done! Cleaned file saved to: {output_file}"
    )
    print(
        f"Unique email records processed: "
        f"{len(seen_emails)}"
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python email_cleaner.py "
            "input.csv output.csv"
        )
        sys.exit(1)

    process_csv(
        sys.argv[1],
        sys.argv[2]
    )
