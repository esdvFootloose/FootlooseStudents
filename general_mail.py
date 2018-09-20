from smtplib import SMTPException
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.html import strip_tags



def send_mail(subject, email_template_name, context, to_email):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    # prepend the marketplace name to the settings
    subject = '{}'.format(subject.strip())
    # generate html email
    html_email = loader.render_to_string(email_template_name, context)
    # attach text and html message
    email_message = EmailMultiAlternatives(subject, strip_tags(html_email), 'website@esdvfootloose.nl', [to_email])
    email_message.attach_alternative(html_email, 'text/html')
    # send
    try:
        email_message.send()
    except SMTPException:
        with open("mailcrash.log", "a") as stream:
            stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))
