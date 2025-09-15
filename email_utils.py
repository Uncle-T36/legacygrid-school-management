import os
import smtplib
from email.mime.text import MIMEText

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def render_template(template_name, context):
    """Render a text template with context values using str.format()."""
    path = os.path.join(TEMPLATE_DIR, template_name)
    with open(path, "r", encoding="utf-8") as f:
        template = f.read()
    return template.format(**context)

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_pass):
    """Send an email using SMTP."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_pass)
        server.sendmail(from_email, [to_email], msg.as_string())

# Example usage
if __name__ == "__main__":
    # Fill in your SMTP and sender details here
    SMTP_DETAILS = {
        "smtp_server": "smtp.yourprovider.com",
        "smtp_port": 465,
        "smtp_user": "your@email.com",
        "smtp_pass": "yourpassword",
        "from_email": "your@email.com",
        "to_email": "recipient@email.com"
    }

    # Choose template and context
    template_name = "email_billing_receipt.txt"
    context = {
        "user_name": "John Doe",
        "amount": "$100",
        "date": "2025-09-15"
    }

    # Render and send
    rendered = render_template(template_name, context)
    subject = rendered.splitlines()[0].replace("Subject: ", "")
    body = "\n".join(rendered.splitlines()[1:])
    send_email(subject, body, SMTP_DETAILS["to_email"],
               SMTP_DETAILS["from_email"],
               SMTP_DETAILS["smtp_server"],
               SMTP_DETAILS["smtp_port"],
               SMTP_DETAILS["smtp_user"],
               SMTP_DETAILS["smtp_pass"])
    print("Email sent!")