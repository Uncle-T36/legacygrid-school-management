# LegacyGrid Automated Email System

Automated email notifications for school events (payments, registrations, etc.), using customizable templates.

## Setup

1. Fill in your SMTP credentials in `smtp_config_example.py`.
2. Add/edit templates in the `templates/` directory.
3. Use `auto_emailer.py` to send emails for different events.

## Example Usage

```python
from auto_emailer import send_event_email
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
```

## Error Logging

All errors are logged in `email_error.log`.

## Extending

- Add more templates to the `templates/` directory.
- Map new events/templates in `TEMPLATE_MAP` in `auto_emailer.py`.