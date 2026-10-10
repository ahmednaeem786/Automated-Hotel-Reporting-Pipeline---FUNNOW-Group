import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Gmail App Password (16 characters)


def send_hotel_report(to_email, hotel_name, message_body):
    """
    Sends an automated performance email to the hotel partner via SMTP.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise ValueError(
            "Missing SENDER_EMAIL or SENDER_PASSWORD in environment variables."
        )

    subject = f"Weekly Performance Update: {hotel_name} x FUNNOW"

    # Compose email
    msg = MIMEMultipart()
    msg["From"] = f"FUNNOW Partner Support <{SENDER_EMAIL}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach plain text body
    msg.attach(MIMEText(message_body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"[SUCCESS] Sent report for {hotel_name} to {to_email}")
        return True
    except Exception as e:
        print(f"[FAILED] Could not send email for {hotel_name}: {e}")
        return False


# Standalone verification
if __name__ == "__main__":
    test_target = SENDER_EMAIL  # Sending test email to self for quick test
    sample_text = (
        "Dear Riverside Hotel Owner,\n\n"
        "Here is your test performance summary from the FUNNOW automated pipeline.\n\n"
        "Best regards,\nFUNNOW Team"
    )
    if test_target:
        send_hotel_report(test_target, "Riverside Hotel (Test)", sample_text)
    else:
        print("Please configure SENDER_EMAIL in your .env file to run this test.")
