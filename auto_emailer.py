import os
from email_utils import load_template, fill_template, send_email

TEMPLATE_MAP = {
    "payment_received": "templates/email_school_fees_receipt.txt",
    "registration_confirmed": "templates/email_registration_confirmation.txt"
    # Add more events/templates here
}

def send_event_email(event, data, recipient, sender, smtp_cfg):
    template_path = TEMPLATE_MAP.get(event)
    if not template_path or not os.path.exists(template_path):
        raise ValueError(f"Template for event '{event}' not found.")
    template = load_template(template_path)
    body = fill_template(template, data)
    # Extract subject from first line
    first_line, *body_lines = body.split('\n', 1)
    subject = first_line.replace("Subject:", "").strip()
    body = body_lines[0] if body_lines else ""
    send_email(subject, body, recipient, sender, smtp_cfg)