import time
import re

from data_processor import process_hotel_data
from llm_manager import generate_hotel_summary
from email_sender import send_hotel_report


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
        df, revenue_threshold, order_thresh = process_hotel_data(
            test_email=recipient_email
        )
        print(f"Data loaded successfully. Processing {len(df)} hotels.\n")
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    for index, row in df.iterrows():
        hotel_name = row["brandname"]
        target_email = row["Boss Gmail"]

        print(f"Processing: {hotel_name}...")

        # Generate AI Message
        email_body = generate_hotel_summary(row.to_dict())

        if "Error" in email_body:
            print(f"[SKIP] AI generation failed for {hotel_name}.\n")
            continue

        # Send Email
        success = send_hotel_report(target_email, hotel_name, email_body)

        # Brief pause to avoid hitting API rate limits on free tiers
        time.sleep(2)

    print("\nPipeline execution finished successfully.")


if __name__ == "__main__":
    main()
