import csv
import re
import sys
from pathlib import Path

import dns.resolver


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


def is_disposable_email(email, disposable_domains):
    """Check whether an email uses a disposable email domain."""
    email = clean_email(email)

    if not is_valid_email(email):
        return False

    domain = email.rsplit("@", 1)[1].lower()
    return domain in disposable_domains


def has_valid_mx(email):
    """
    Check whether the email domain has an MX record.

    Returns:
        True  - MX record exists
        False - domain has no usable MX record
        None  - DNS lookup failed temporarily or unexpectedly
    """
    email = clean_email(email)

    if not is_valid_email(email):
        return False

    domain = email.rsplit("@", 1)[1]

    try:
        answers = dns.resolver.resolve(
            domain,
            "MX",
            lifetime=5
        )

        return len(answers) > 0

    except (
        dns.resolver.NXDOMAIN,
        dns.resolver.NoAnswer,
    ):
        return False

    except (
        dns.resolver.Timeout,
        dns.resolver.NoNameservers,
    ):
        return None

    except Exception:
        return None


def process_csv(
    input_file,
    output_file,
    check_disposable=True,
    check_mx=True
):
    """
    Clean emails, remove duplicates, validate format,
    detect disposable emails, and check MX records.

    The input CSV must contain a column named 'email'.
    """

    seen_emails = set()

    disposable_domains = (
        load_disposable_domains()
        if check_disposable
        else set()
    )

    with open(
        input_file,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        if not reader.fieldnames:
            raise ValueError("Input CSV has no header row.")

        email_column = None

        for column in reader.fieldnames:
            if column.strip().lower() == "email":
                email_column = column
                break

        if email_column is None:
            raise ValueError(
                "Input CSV must contain a column named 'email'."
            )

        fieldnames = list(reader.fieldnames)

        if "email_status" not in fieldnames:
            fieldnames.append("email_status")

        if "disposable_email" not in fieldnames:
            fieldnames.append("disposable_email")

        if "mx_status" not in fieldnames:
            fieldnames.append("mx_status")

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

                # Skip blank emails
                if not email:
                    continue

                # Remove duplicates
                if email in seen_emails:
                    continue

                seen_emails.add(email)

                # Save cleaned email
                row[email_column] = email

                # Basic format validation
                valid_format = is_valid_email(email)

                row["email_status"] = (
                    "valid_format"
                    if valid_format
                    else "invalid_format"
                )

                # Disposable email detection
                if check_disposable and valid_format:

                    row["disposable_email"] = (
                        "yes"
                        if is_disposable_email(
                            email,
                            disposable_domains
                        )
                        else "no"
                    )

                elif check_disposable:
                    row["disposable_email"] = "unknown"

                else:
                    row["disposable_email"] = "not_checked"

                # MX / domain validation
                if check_mx and valid_format:

                    mx_result = has_valid_mx(email)

                    if mx_result is True:
                        row["mx_status"] = "valid_mx"

                    elif mx_result is False:
                        row["mx_status"] = "no_mx"

                    else:
                        row["mx_status"] = "dns_error"

                elif check_mx:
                    row["mx_status"] = "invalid_format"

                else:
                    row["mx_status"] = "not_checked"

                writer.writerow(row)

    print(
        f"Done! Cleaned file saved to: "
        f"{output_file}"
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
