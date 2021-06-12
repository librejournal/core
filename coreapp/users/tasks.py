from coreapp.coreapp.celery import app
from coreapp.users.verification.email import (
    send_simple_verification_mail_with_verif_url,
)


@app.task()
def send_simple_verification_mail_task(to, token_key, verification_url):
    send_simple_verification_mail_with_verif_url(to, token_key, verification_url)
