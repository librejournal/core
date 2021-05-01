from django.core.mail import send_mail

from coreapp.utils.global_request import get_current_request

def _build_verification_url(token_key):
    request = get_current_request()
    domain = request.request.build_absolute_uri("/")
    return f"{domain}api/auth/verification?token={token_key}"

def send_simple_verification_mail(to, token_key):
    verification_url = _build_verification_url(token_key)
    email_content = \
f'''
    Your verification url;
    {verification_url}
'''
    send_mail(
        "librejournal user verification",
        email_content,
        "berkkarahan00@gmail.com",
        [to],
    )
