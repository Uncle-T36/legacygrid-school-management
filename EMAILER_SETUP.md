## Automated Emailer Setup

This repository includes an automated emailer for school events (e.g., payment received, registration confirmation).

### Configuration

1. Copy `smtp_config_example.py` to `smtp_config.py` and fill in your SMTP details:
    - **server**: Your SMTP provider (e.g., smtp.gmail.com).
    - **port**: Use 465 for SSL or 587 for TLS.
    - **user**: Your sender email address.
    - **password**: Your email password or app password.

2. Edit the templates in the `templates/` directory as needed.

3. Use `auto_emailer.py` to send event-driven emails.

### Running the Tests

Run unit tests with:
```bash
python -m unittest test_auto_emailer.py
```

### Adding New Event Templates

- Add a new template file under `templates/`.
- Update the `TEMPLATE_MAP` in `auto_emailer.py` with the event name and template path.

### Logging

All errors are logged to `email_error.log`.

### Security Note

Never commit real SMTP credentials to the repository. Use environment variables or secure secrets management for production.

### Example Usage

See the bottom of `auto_emailer.py` for example usage.