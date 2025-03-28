import streamlit as st
from email_fetcher import connect_email, fetch_today_emails
from email_classifier import classify_email
from email_summarizer import summarize_email

st.title("📩 AI Email Summarizer")

# User Login
email_id = st.text_input("📧 Enter your email ID:")
app_password = st.text_input("🔑 Enter your App Password:", type="password")
login_button = st.button("Login & Fetch Emails")

if login_button and email_id and app_password:
    mail = connect_email(email_id, app_password)
    
    if mail:
        emails = fetch_today_emails(mail)
        if emails:
            categorized_emails = {}
            for email_data in emails:
                category = classify_email(email_data["body"])
                if category not in categorized_emails:
                    categorized_emails[category] = []
                categorized_emails[category].append(email_data)
            
            for category, email_list in categorized_emails.items():
                st.subheader(f"📂 {category} ({len(email_list)} emails)")
                for email_data in email_list:
                    st.markdown(f"📌 **Subject:** {email_data['subject']}")
                    st.markdown(f"✉️ **From:** {email_data['sender']}")
                    summary = summarize_email(email_data["body"])
                    st.write(f"📝 **Summary:** {summary}")
        else:
            st.error("No emails received today.")
    else:
        st.error("Login failed! Check your credentials.")
