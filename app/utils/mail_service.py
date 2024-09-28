from flask import render_template
from app import app

import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(template: str, title: str, message: str, to_email: str, docx_file_path: str, from_name: str = "Voice2Issue Deviniti"):
    html = render_template(template, message=message)

    message = MIMEMultipart()
    message["From"] = formataddr(
        (
            str(Header(from_name, "utf-8")),
            app.config["MAIL_DEFAULT_SENDER"],
        )
    )
    message["To"] = to_email
    message["Subject"] = Header(title, "utf-8")
    message.attach(MIMEText(html, "html", "utf-8"))

    if docx_file_path:
        with open(docx_file_path, "rb") as file:
            part = MIMEApplication(file.read(), Name=os.path.basename(docx_file_path))
        part[
            "Content-Disposition"
        ] = f'attachment; filename="{os.path.basename(docx_file_path)}"'
        message.attach(part)

    try:
        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            server.set_debuglevel(0)
            if app.config["MAIL_USE_TLS"]:
                server.starttls()
            server.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            server.sendmail(
                app.config["MAIL_DEFAULT_SENDER"],
                to_email,
                message.as_string().encode("utf-8"),
            )
            return True
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")
        return False
