import smtplib
from email.mime.text import MIMEText
import os

def load_template(template_name):
    with open(os.path.join('templates', template_name), 'r') as f:
        return f.read()

def fill_template(template_str, context):
    filled = template_str
    for key, value in context.items():
        filled = filled.replace(f"{{{{{key}}}}}", str(value))
    return filled

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, [to_email], msg.as_string())