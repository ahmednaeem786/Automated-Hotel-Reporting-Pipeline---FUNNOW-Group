import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr

from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")  # Gmail App Password (16 characters)


class EmailConfigurationError(RuntimeError):
    """Raised when SMTP credentials are not configured."""


class EmailInputError(ValueError):
    """Raised when an email report contains invalid input."""


def send_hotel_report(to_email, hotel_name, message_body):
    """
    Sends an automated performance email to the hotel partner via SMTP.
    """
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise EmailConfigurationError(
            "Missing SENDER_EMAIL or SENDER_PASSWORD. "
            "Add both values to the environment or .env file."
        )
    parsed_email = parseaddr(to_email)[1] if isinstance(to_email, str) else ""
    if (
        not isinstance(to_email, str)
        or parsed_email != to_email
        or "@" not in parsed_email
        or "." not in parsed_email.rsplit("@", 1)[-1]
    ):
        raise EmailInputError(f"Invalid recipient email address: {to_email!r}")
    if not isinstance(hotel_name, str) or not hotel_name.strip():
        raise EmailInputError("Hotel name must be a non-empty string.")
    if not isinstance(message_body, str) or not message_body.strip():
        raise EmailInputError("Email message body must be a non-empty string.")

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
    except smtplib.SMTPAuthenticationError as error:
        print(f"[FAILED AUTHENTICATION] {hotel_name}: check SMTP credentials ({error})")
    except smtplib.SMTPRecipientsRefused as error:
        print(f"[FAILED RECIPIENT] {hotel_name}: recipient rejected ({error})")
    except smtplib.SMTPSenderRefused as error:
        print(f"[FAILED SENDER] {hotel_name}: sender rejected ({error})")
    except smtplib.SMTPConnectError as error:
        print(f"[FAILED CONNECTION] {hotel_name}: SMTP server unavailable ({error})")
    except smtplib.SMTPServerDisconnected as error:
        print(
            f"[FAILED DISCONNECTED] {hotel_name}: SMTP server closed the connection ({error})"
        )
    except (smtplib.SMTPDataError, smtplib.SMTPException) as error:
        print(f"[FAILED SMTP] {hotel_name}: message was not accepted ({error})")
    except OSError as error:
        print(f"[FAILED NETWORK] {hotel_name}: network error ({error})")
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
