import getpass
from email_utils import render_template, send_email

def main():
    print("LegacyGrid Email Tester")
    template_choices = [
        "email_billing_receipt.txt",
        "email_password_reset.txt",
        "email_welcome.txt",
        "email_school_fees_receipt.txt"
    ]
    print("Available templates:")
    for i, tmpl in enumerate(template_choices):
        print(f"{i+1}. {tmpl}")
    choice = int(input("Select a template (1-4): ")) - 1
    template_name = template_choices[choice]

    # Collect context variables
    context = {}
    print("Enter template variables (leave blank to skip):")
    with open(f"templates/{template_name}") as f:
        for line in f:
            # Detect variables in template: {{variable}}
            while "{{" in line and "}}" in line:
                start = line.find("{{") + 2
                end = line.find("}}")
                var = line[start:end].strip()
                if var not in context:
                    context[var] = input(f"{var}: ") or f"<{{var}}>"
                line = line[end+2:]  # Continue to find more variables in the line

    smtp_server = input("SMTP server (e.g., smtp.gmail.com): ")
    smtp_port = int(input("SMTP port (e.g., 465): "))
    from_email = input("Your email: ")
    smtp_user = input("SMTP username (often same as email): ")
    smtp_pass = getpass.getpass("SMTP password: ")
    to_email = input("Recipient email: ")

    rendered = render_template(template_name, context)
    subject = rendered.splitlines()[0].replace("Subject: ", "")
    body = "\n".join(rendered.splitlines()[1:])
    send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_pass)
    print(f"Sent '{subject}' to {to_email}")

if __name__ == "__main__":
    main()