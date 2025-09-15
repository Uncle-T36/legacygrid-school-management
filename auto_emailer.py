import smtplib
from email.mime.text import MIMEText
from string import Template
import os
import logging

# Logging setup
logging.basicConfig(filename='email_error.log', level=logging.ERROR)

# Map event types to templates
TEMPLATE_MAP = {
    "payment_received": "templates/email_school_fees_receipt.txt",
    "registration_confirmation": "templates/email_registration_confirmation.txt"
}

def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return Template(f.read())

def send_event_email(event_type, data, to_email, from_email, smtp_cfg):
    template_path = TEMPLATE_MAP.get(event_type)
    if not template_path or not os.path.exists(template_path):
        logging.error(f"Template for event '{event_type}' not found.")
        return False

    template = load_template(template_path)
    message_text = template.safe_substitute(data)
    subject_line = message_text.splitlines()[0].replace("Subject: ", "")
    body = "\n".join(message_text.splitlines()[1:]).strip()

    msg = MIMEText(body)
    msg['Subject'] = subject_line
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        with smtplib.SMTP(smtp_cfg['server'], smtp_cfg['port']) as server:
            server.starttls()
            server.login(smtp_cfg['user'], smtp_cfg['password'])
            server.sendmail(from_email, [to_email], msg.as_string())
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    from smtp_config_example import smtp_cfg
    send_event_email(
        "payment_received",
        {
            "student_name": "Jane Doe",
            "parent_name": "John Doe",
            "amount": "500",
            "date": "2025-09-15"
        },
        "parent@email.com",
        "your@email.com",
        smtp_cfg
    )