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