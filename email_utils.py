import smtplib
from email.mime.text import MIMEText
from string import Template

def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return Template(f.read())

def fill_template(template, data):
    return template.safe_substitute(data)

def send_email(subject, body, recipient, sender, smtp_cfg):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    try:
        with smtplib.SMTP(smtp_cfg["server"], smtp_cfg["port"]) as server:
            server.starttls()
            server.login(smtp_cfg["user"], smtp_cfg["password"])
            server.sendmail(sender, [recipient], msg.as_string())
    except Exception as e:
        with open('email_error.log', 'a') as log:
            log.write(str(e) + '\n')
        raise
