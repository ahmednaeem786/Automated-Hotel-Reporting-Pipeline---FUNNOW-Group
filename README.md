# FUNNOW Automated Hotel Reporting Pipeline

An automated weekly hotel performance reporting pipeline for FUNNOW Group. The
application reads hotel performance data from a CSV file, calculates a simple
performance assessment, asks Groq to write a personalized summary, and sends
the result by email through Gmail SMTP.

## What It Does

For each hotel in the input dataset, the pipeline:

1. Finds and loads a compatible CSV dataset.
2. Calculates median revenue and median order thresholds.
3. Assigns one of three performance statuses:
	 - `Performing Well`: revenue and orders are both at or above their medians.
	 - `Needs Improvement`: revenue and orders are both below their medians.
	 - `Mixed Results`: one metric is above its median and the other is below it.
4. Generates a three- to four-sentence performance email with Groq.
5. Sends the email using Gmail SMTP over TLS.
6. Reports failures clearly and continues with other hotels where possible.

The pipeline pauses for two seconds after each successful email to reduce the
chance of hitting free-tier API or mail-service limits.

## Project Structure

```text
.
├── data/
│   └── hotel report CSV file
├── data_processor.py       # Dataset discovery, loading, and performance logic
├── email_sender.py         # Gmail SMTP composition and delivery
├── llm_manager.py          # Groq prompt construction and AI summary generation
├── main.py                 # Interactive pipeline entry point
├── requirements.txt        # Python dependencies
└── README.md
```

## Requirements

- Python 3.9 or newer
- A Groq API key
- A Gmail account with an App Password enabled
- Network access to the Groq API and Gmail SMTP

The application does not use a web server or database. Its state is kept in
memory for the duration of one run, and the generated messages are sent
directly by email.

## Installation

From the project directory, create and activate a virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. Do not commit this file or expose its
values in source control.

```dotenv
GROQ_API_KEY=your_groq_api_key
SENDER_EMAIL=your_gmail_address@gmail.com
SENDER_PASSWORD=your_gmail_app_password
```

### Groq configuration

`GROQ_API_KEY` is used by `llm_manager.py`. The configured model is:

```text
qwen/qwen3.8-27b
```

The application checks for a missing key before making an API request and stops
cleanly with an actionable configuration message.

### Gmail configuration

`SENDER_EMAIL` is the Gmail address used as the sender. `SENDER_PASSWORD` must
be a Gmail App Password, not the normal Gmail account password. Gmail SMTP is
configured as follows:

```text
Server: smtp.gmail.com
Port: 587
Security: STARTTLS
```

To use an App Password, the Google account generally needs two-step
verification enabled. Follow your organization's security policy when
creating and storing credentials.

## Running the Pipeline

Activate the virtual environment and run:

```powershell
python main.py
```

The program asks where reports should be sent:

```text
Enter the email address to receive the reports
(press Enter for the default assessment address):
```

An invalid or empty response falls back to the default address currently
defined in `main.py`. For a real run, enter the intended recipient explicitly.

### Important recipient behavior

The current implementation uses the interactive recipient for every report in
the run. `data_processor.py` assigns that value to the generated `Boss Gmail`
column, so the email addresses present in the CSV are not used for delivery.
This is useful for assessment and testing because it prevents accidental
emails to real hotel contacts. A production version should replace this with a
clear opt-in mode or use each row's verified recipient address.

## Dataset Format

By default, the program searches recursively below the project directory for a
CSV containing these required columns:

```text
brandname,revenue,Order
```

The bundled sample data includes those fields plus `Boss Gmail`. Revenue and
order values must be numeric because their medians are used for classification.

The header matching is whitespace-tolerant, but column names are otherwise
case-sensitive. The generated columns are:

| Column | Meaning |
| --- | --- |
| `performance_status` | Status calculated from median revenue and order thresholds |
| `Boss Gmail` | Recipient assigned by the `test_email` argument in the current implementation |

### Selecting a specific dataset

Set `HOTEL_DATA_FILE` in `.env` or the shell environment when the dataset is
outside the project directory or when multiple compatible CSV files exist:

```dotenv
HOTEL_DATA_FILE=C:\path\to\hotel-report.csv
```

The configured path must point to an existing file. Without this variable:

- No compatible CSV produces a clear `FileNotFoundError` message.
- Multiple compatible CSVs produce a message listing the matches and asking you
	to set `HOTEL_DATA_FILE`.
- CSV files under `.git`, `.venv`, `venv`, `__pycache__`, or `node_modules` are
	ignored during discovery.

## Email Content

The generated message is a plain-text email with this subject pattern:

```text
Weekly Performance Update: <hotel name> x FUNNOW
```

The Groq prompt asks for:

- Three to four sentences.
- No subject line or email headers in the generated body.
- A flash-promotion suggestion for `Needs Improvement` hotels.
- A congratulations message and weekend-inventory reminder for `Performing Well` hotels.
- A sign-off from the FUNNOW Account Management Team.

`Mixed Results` is supported by the data processor, although the prompt does
not prescribe a special recommendation for that status.

## Error Handling

The pipeline is designed to fail clearly at the appropriate scope:

- Dataset discovery and parsing errors stop the run before any emails are sent.
- Missing Groq credentials stop the run with an AI configuration message.
- Missing required hotel fields skip only the affected hotel.
- Groq authentication, rate-limit, connection, timeout, API, and empty-response
	failures skip the affected hotel.
- Missing SMTP credentials stop the run because no report can be delivered.
- Invalid recipient or message input skips the affected hotel.
- SMTP authentication, recipient, sender, connection, disconnection, network,
	and message-rejection failures are reported and do not crash the process.

The program does not currently retry failed Groq or SMTP requests. A failed
hotel should be reviewed and retried in a later run after the reported cause is
resolved.

## Running Individual Components

Each module has a small standalone entry point for manual checks.

```powershell
python data_processor.py
python llm_manager.py
python email_sender.py
```

The `llm_manager.py` check makes a real Groq request when credentials are
configured. The `email_sender.py` check sends a real test email to
`SENDER_EMAIL`, so use it only when that behavior is intended.

## Troubleshooting

### `GROQ_API_KEY is missing`

Confirm that `.env` is in the same directory as `main.py`, that the variable is
spelled exactly as `GROQ_API_KEY`, and that the virtual environment is active.

### Groq authentication or rate-limit failure

Check that the key is valid, the account has access to the configured model,
and the account has remaining quota. Rate-limit failures are not retried
automatically.

### SMTP authentication failure

Confirm the sender address and Gmail App Password. Do not use the normal Gmail
password, and do not include spaces in the App Password unless the provider
specifically requires them.

### No dataset found

Confirm that a CSV exists below the project directory and that its header
contains `brandname`, `revenue`, and `Order`. Use `HOTEL_DATA_FILE` to select a
specific file.

### Reports are sent to the wrong place

Remember that the address entered at startup currently replaces the dataset's
recipient addresses for the entire run. Stop the run and restart it with the
intended address.

## Security Notes

- Keep `.env`, API keys, App Passwords, and real recipient data private.
- Use a dedicated Gmail account or service identity for automated delivery when
	appropriate.
- Test with a controlled recipient before sending production reports.
- Review generated AI content before adopting this pipeline for unsupervised
	customer communication.
- The sample dataset may contain personal or business contact information;
	handle it according to your organization's privacy requirements.

## Current Limitations

- No automated test suite is included yet.
- No retry or backoff strategy is implemented for transient API or SMTP errors.
- The sender recipient is a single run-wide address rather than a per-hotel
	verified destination.
- AI output is checked for presence but is not validated for exact sentence
	count, tone, or prompt compliance.
- There is no persistent delivery log beyond console output.

## Suggested Production Improvements

Before using this as an unattended production job, consider adding:

1. Automated unit tests for dataset classification, prompt inputs, and failure paths.
2. Retries with exponential backoff for transient Groq and SMTP failures.
3. Structured logging and a delivery report with sent, skipped, and failed counts.
4. A dry-run mode that generates messages without sending them.
5. Per-hotel recipient validation and an explicit confirmation step before delivery.
6. Secret management through the deployment environment rather than a local `.env` file.
7. A scheduler such as Task Scheduler, cron, or a managed workflow service.
