import re
import time

from data_processor import process_hotel_data
from email_sender import EmailConfigurationError, EmailInputError, send_hotel_report
from llm_manager import LLMConfigurationError, LLMInputError, generate_hotel_summary

DEFAULT_TEST_EMAIL = "ahmednaeembhuri456@gmail.com"
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_recipient_email():
    """Ask for a report recipient and fall back to the assessment email."""
    try:
        entered_email = input(
            "Enter the email address to receive the reports "
            f"(press Enter for {DEFAULT_TEST_EMAIL}): "
        ).strip()
    except EOFError:
        entered_email = ""

    if entered_email and EMAIL_PATTERN.fullmatch(entered_email):
        print(f"Reports will be sent to {entered_email}.\n")
        return entered_email

    if entered_email:
        print(
            f"That email address is invalid. Reports will be sent to "
            f"{DEFAULT_TEST_EMAIL} instead.\n"
        )
    else:
        print(f"No email entered. Reports will be sent to {DEFAULT_TEST_EMAIL}.\n")

    return DEFAULT_TEST_EMAIL


def main():
    print("Starting FUNNOW Hotel AI Reporting Pipeline...\n")

    recipient_email = get_recipient_email()

    # 1. Ingest Data & Apply Logic
    try:
        df, _, _ = process_hotel_data(test_email=recipient_email)
        print(f"Data loaded successfully. Processing {len(df)} hotels.\n")
    except (
        FileNotFoundError,
        KeyError,
        NotADirectoryError,
        OSError,
        RuntimeError,
        UnicodeDecodeError,
        ValueError,
    ) as error:
        print(f"Failed to load data: {error}")
        return

    for index, row in df.iterrows():
        hotel_name = row["brandname"]
        target_email = row["Boss Gmail"]

        print(f"Processing: {hotel_name}...")

        # Generate AI Message
        try:
            email_body = generate_hotel_summary(row.to_dict())
        except LLMConfigurationError as error:
            print(f"[STOP] AI configuration error: {error}")
            return
        except LLMInputError as error:
            print(f"[SKIP] Invalid hotel data for {hotel_name}: {error}\n")
            continue

        if (
            not email_body
            or not email_body.strip()
            or email_body.startswith("Error generating AI summary.")
        ):
            print(
                f"[SKIP] AI generation failed or returned empty content for {hotel_name}.\n"
            )
            continue

        # Send Email
        try:
            success = send_hotel_report(target_email, hotel_name, email_body)
        except EmailConfigurationError as error:
            print(f"[STOP] Email configuration error: {error}")
            return
        except EmailInputError as error:
            print(f"[SKIP] Invalid email report for {hotel_name}: {error}\n")
            continue

        if not success:
            print(f"[SKIP] Email was not sent for {hotel_name}.\n")
            continue

        # Brief pause to avoid hitting API rate limits on free tiers
        time.sleep(2)

    print("\nPipeline execution finished successfully.")


if __name__ == "__main__":
    main()
