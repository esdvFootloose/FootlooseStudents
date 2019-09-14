from smtplib import SMTPException
from django.core import mail
from django.template import loader
from django.utils.html import strip_tags
import smtplib

from django.core.mail.utils import DNS_NAME
from django.core.mail.backends.smtp import EmailBackend


def build_mail(subject, email_template_name, context, to_email):
    """
    Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    """
    # prepend the marketplace name to the settings
    subject = '{}'.format(subject.strip())
    # generate html email
    html_email = loader.render_to_string(email_template_name, context)
    # attach text and html message
    email_message = mail.EmailMultiAlternatives(subject, strip_tags(html_email), 'website@esdvfootloose.nl', [to_email])
    email_message.attach_alternative(html_email, 'text/html')
    return email_message
    # # send
    # try:
    #     email_message.send()
    # except SMTPException:
    #     with open("mailcrash.log", "a") as stream:
    #         stream.write("Mail to {} could not be send:\n{}\n".format(to_email, html_email))

def send_mail(emails):
    connection = mail.get_connection()
    connection.send_messages(emails)


class SSLEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        try:
            self.connection = smtplib.SMTP_SSL(self.host, self.port,
                                               local_hostname=DNS_NAME.get_fqdn())
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except:
            if not self.fail_silently:
                raise
