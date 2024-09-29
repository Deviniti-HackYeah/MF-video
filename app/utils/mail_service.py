from flask import render_template
from app import app

import smtplib
from email.header import Header
from email.utils import formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

def send_email(template: str, title: str, message: str, to_email: str, from_name: str = "Kuras Theliver"):
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

    try:
        with smtplib.SMTP_SSL(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]) as server:
            server.set_debuglevel(0)
            server.login(app.config["MAIL_USERNAME"], os.getenv("MAIL_PASSWORD", ""))
            server.sendmail(
                app.config["MAIL_DEFAULT_SENDER"],
                to_email,
                message.as_string().encode("utf-8"),
            )
            return True
    except Exception as e:
        print(f"Błąd podczas wysyłania e-maila: {e}")
        return False
