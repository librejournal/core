from coreapp.coreapp.celery import app
from coreapp.users.verification.email import (
    send_simple_verification_mail_with_verif_url,
    send_simple_password_reset_with_url,
)


@app.task()
def send_simple_verification_mail_task(to, token_key, verification_url):
    send_simple_verification_mail_with_verif_url(to, token_key, verification_url)


@app.task()
def send_simple_password_reset_mail_task(to, token_key, password_reset_url):
    send_simple_password_reset_with_url(to, token_key, password_reset_url)
