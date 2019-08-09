from django.contrib.auth.tokens import PasswordResetTokenGenerator
from FootlooseStudents.secret import DATABASE_PASSWORD_IMPORT
from .models import VerifyToken
from .wordpress import WordPress
from django.conf import settings
from general_mail import send_mail

class VerifyTokenGenerator(PasswordResetTokenGenerator):
    key_salt = DATABASE_PASSWORD_IMPORT
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + user.email + str(timestamp)

    def make_token(self, user):
        data = WordPress.get_students_data(user.username, as_dict=True)[1][0]
        email = data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific']
        token = super().make_token(user)
        try:
            tokenmodel = user.verifytoken
        except:
            tokenmodel = VerifyToken(user=user, token=token, email=email)
        tokenmodel.token = token
        tokenmodel.email = email
        tokenmodel.save()
        return token

    def check_token(self, user, token):
        if not super().check_token(user, token):
            return False
        try:
            tokenmodel = user.verifytoken
        except:
            return False

        data = WordPress.get_students_data(user.username, as_dict=True)[1][0]
        email = data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else \
        data['footloose_fontys_verific']

        if tokenmodel.token != token or tokenmodel.email != email:
            return False

        return True

def send_student_verification_mail(user):
    props, data = WordPress.get_students_data(user.username, as_dict=True)
    data = data[0]
    generator = VerifyTokenGenerator()
    token = generator.make_token(user)

    url = "{}/students/verify/confirm/{}/".format(settings.DOMAIN, token)

    send_mail('Footloose Student Verification', 'mail/verify.html', {'url' : url}, data['footloose_tuemail_verific'] if data['footloose_institution'] == 'Eindhoven University of Technology' else data['footloose_fontys_verific'])