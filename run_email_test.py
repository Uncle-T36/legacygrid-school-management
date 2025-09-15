import os
from email_utils import load_template, fill_template, send_email

def get_available_templates():
    return [f for f in os.listdir('templates') if f.endswith('.txt')]

def prompt_template_vars(template_content):
    import re
    vars = re.findall(r'{{(.*?)}}', template_content)
    context = {}
    for var in set(vars):
        context[var] = input(f'Enter value for {var}: ')
    return context

def main():
    print("LegacyGrid Email Test Utility\n")
    templates = get_available_templates()
    print("Available templates:")
    for i, tname in enumerate(templates):
        print(f"{i+1}. {tname}")
    tindex = int(input("Select a template by number: ")) - 1
    template_name = templates[tindex]
    template_content = load_template(template_name)
    context = prompt_template_vars(template_content)
    filled = fill_template(template_content, context)
    subject_line = filled.splitlines()[0].replace('Subject:', '').strip()
    body = '\n'.join(filled.splitlines()[1:]).strip()
    print("\nSample email preview:")
    print("-" * 40)
    print(f"Subject: {subject_line}")
    print(body)
    print("-" * 40)

    send_it = input("Send this email? (y/N): ").lower()
    if send_it == 'y':
        to_email = input("Recipient email: ")
        from_email = input("Sender email: ")
        smtp_server = input("SMTP server (e.g. smtp.gmail.com): ")
        smtp_port = int(input("SMTP port (e.g. 587): "))
        smtp_user = input("SMTP username: ")
        smtp_password = input("SMTP password: ")
        send_email(subject_line, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password)
        print("Email sent!")

if __name__ == '__main__':
    main()