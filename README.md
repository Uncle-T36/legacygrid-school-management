# LegacyGrid Automated Email System

This module automates emails for school events (payments, registrations, etc.) using templated messages.

## Setup

1. Place your SMTP credentials in `smtp_config_example.py` (rename/copy as needed).
2. Add/edit templates in the `templates/` directory (`.txt` files).
3. Use `auto_emailer.py` for sending emails based on events.

## Usage Example

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

Any errors will be logged in `email_error.log`.

## Extending

- Add more templates and map them in `TEMPLATE_MAP` in `auto_emailer.py`.
- Customize templates with additional fields as needed.
