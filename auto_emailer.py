import os
from email_utils import load_template, fill_template, send_email

# Mapping event types to template files
TEMPLATE_MAP = {
    "payment_received": "email_school_fees_receipt.txt",
    "registration_complete": "email_registration_confirmation.txt",
    # Extend with more event->template mappings as needed
}

def send_event_email(event_type, context, to_email, from_email, smtp_config, log_errors=True):
    """Send an email based on event type and context dict."""
    try:
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
    except Exception as e:
        if log_errors:
            with open("email_error.log", "a") as logf:
                logf.write(f"[{event_type}] {str(e)}\n")
        print(f"Error sending email for event '{event_type}': {e}")

# EXAMPLE USAGE:
# from smtp_config_example import smtp_cfg
# send_event_email(
#     "payment_received",
#     {"student_name": "Jane Doe", "amount": "500", "date": "2025-09-15"},
#     "parent@email.com",
#     "your@email.com",
#     smtp_cfg
# )
