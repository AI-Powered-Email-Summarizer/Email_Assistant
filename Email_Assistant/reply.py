import streamlit as st
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configure Gemini AI API Key
genai.configure(api_key="AIzaSyASwoRCdWRs4W4P05zmXSHpI-Xwd2fIxkQ")

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]

# 📌 Authenticate Gmail API
@st.cache_resource
def authenticate_gmail_api():
    creds = None
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=8080)
    return build("gmail", "v1", credentials=creds)

# 📌 Get Unread Emails (Excluding Mail Delivery Failures)
@st.cache_data(ttl=300)  # Cache for 5 mins
def get_unread_emails():
    service = authenticate_gmail_api()
    results = service.users().messages().list(userId="me", labelIds=["INBOX"], q="is:unread").execute()
    messages = results.get("messages", [])

    email_list = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        headers = msg["payload"]["headers"]

        subject = next((header["value"] for header in headers if header["name"] == "Subject"), "No Subject")
        sender = next((header["value"] for header in headers if header["name"] == "From"), "Unknown Sender")

        # 📌 Exclude Delivery Failure Notifications
        if "mailer-daemon@googlemail.com" not in sender.lower():
            email_list.append({"id": message["id"], "subject": subject, "sender": sender})

    return email_list

# 📌 Generate AI Reply
@st.cache_data(ttl=600)  # Cache AI response for 10 minutes
def generate_ai_response(subject):
    model = genai.GenerativeModel("gemini-2.0-flash-thinking-exp")
    prompt = f"Generate a short professional reply for an email with this subject: {subject}"
    response = model.generate_content(prompt)
    return response.text if response else "Sorry, I couldn't generate a response."

# 📌 Create message function to send emails
def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    msg = MIMEText(message_text)
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

# 📌 Streamlit UI
st.title("📧 AI Email Auto-Reply System")

email_list = get_unread_emails()
email_subjects = [f"{email['sender']} - {email['subject']}" for email in email_list]

selected_index = st.selectbox("Select an unread email to reply:", range(len(email_subjects)), format_func=lambda x: email_subjects[x])

if selected_index is not None:
    selected_email = email_list[selected_index]
    st.subheader("Selected Email")
    st.write(f"**From:** {selected_email['sender']}")
    st.write(f"**Subject:** {selected_email['subject']}")

    if "reply_content" not in st.session_state:
        st.session_state["reply_content"] = ""

    if st.button("Generate Reply"):
        st.session_state["reply_content"] = generate_ai_response(selected_email["subject"])

    reply_content = st.text_area("Generated Reply:", st.session_state["reply_content"], height=150)

    if st.button("Send Reply"):
        service = authenticate_gmail_api()
        sender = "your_email@gmail.com"  # Your email address
        to = selected_email["sender"]  # The sender of the email you're replying to
        subject = f"Re: {selected_email['subject']}"
        
        # Use the create_message function to format the email
        encoded_message = create_message(sender, to, subject, reply_content)
        
        try:
            # Send the email using the Gmail API
            service.users().messages().send(userId="me", body=encoded_message).execute()
            st.success("✅ Reply Sent!")
        except Exception as e:
            st.error(f"Error sending email: {e}")

    if st.button("Don't Send"):
        st.warning("Reply not sent.")
