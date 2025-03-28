import imaplib
import email
from email.header import decode_header
import datetime

def connect_email(email_id, app_password):
    """Connects to the email inbox securely."""
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_id, app_password)
        mail.select("inbox")
        return mail
    except Exception as e:
        print(f"❌ Error connecting to email: {str(e)}")
        return None

def fetch_today_emails(mail):
    """Fetches today's emails."""
    try:
        today = datetime.datetime.today().strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SENTON {today})')
        email_ids = messages[0].split()
        emails = []

        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8", errors="ignore")

                    sender = msg.get("From", "Unknown Sender")
                    date = msg.get("Date", "Unknown Date")
                    body = msg.get_payload(decode=True).decode(errors="ignore")

                    emails.append({"date": date, "sender": sender, "subject": subject, "body": body})
        return emails
    except Exception as e:
        print(f"⚠️ Error fetching emails: {str(e)}")
        return []
