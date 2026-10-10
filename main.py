import time
from data_processor import process_hotel_data
from llm_manager import generate_hotel_summary
from email_sender import send_hotel_report


def main():
    print("Starting FUNNOW Hotel AI Reporting Pipeline...\n")

    # 1. Ingest Data & Apply Logic
    try:
        # Defaults to the test email you set in data_processor.py
        df, revenue_threshold, order_thresh = process_hotel_data()
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
