import os
from email_utils import load_template, fill_template, send_email

# Mapping event types to template files
TEMPLATE_MAP = {
    "payment_received": "email_school_fees_receipt.txt",
    "registration_complete": "email_registration_confirmation.txt",
    # Add more event->template mappings as needed
}

def send_event_email(event_type, context, to_email, from_email, smtp_config):
    """Send an email based on event type and context dict."""
    template_file = TEMPLATE_MAP.get(event_type)
    if not template_file:
        raise ValueError(f"No template mapped for event type: {event_type}")
    template_path = os.path.join('templates', template_file)
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")
    template_content = load_template(template_file)
    filled = fill_template(template_content, context)
    subject_line = filled.splitlines()[0].replace('Subject:', '').strip()
    body = '\n'.join(filled.splitlines()[1:]).strip()
    send_email(
        subject_line,
        body,
        to_email,
        from_email,
        smtp_config['server'],
        smtp_config['port'],
        smtp_config['user'],
        smtp_config['password']
    )
    print(f"Email for event '{event_type}' sent to {to_email}.")

# EXAMPLE USAGE (to be used in your backend code):
# smtp_cfg = {
#     "server": "smtp.gmail.com", "port": 587,
#     "user": "your@email.com", "password": "yourpassword"
# }
# send_event_email(
#     "payment_received",
#     {"student_name": "Jane Doe", "amount": "500", "date": "2025-09-15"},
#     "parent@email.com",
#     "your@email.com",
#     smtp_cfg
# )