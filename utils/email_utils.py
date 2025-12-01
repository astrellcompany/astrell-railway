import resend
from django.conf import settings

def send_resend_email(to, subject, html):
    """ Send email using Resend API """
    resend.api_key = settings.RESEND_API_KEY

    return resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": to if isinstance(to, list) else [to],
        "subject": subject,
        "html": html
    })
