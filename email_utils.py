import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def load_template(template_name):
    template_path = os.path.join('templates', template_name)
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def fill_template(template_str, context):
    for key, value in context.items():
        template_str = template_str.replace(f'{{{{{key}}}}}', str(value))
    return template_str

def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_email, to_email, msg.as_string())