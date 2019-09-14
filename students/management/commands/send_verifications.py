from django.core.management.base import BaseCommand
from students.wordpress import WordPress
from django.contrib.auth.models import User
from students.models import StudentMeta, VerifyToken
from students.util import send_student_verification_mail
from general_util import get_academic_year
from django.db.models import Q

class Command(BaseCommand):
    help = 'sync new subscriptions and users and send verification mails'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.clean_tokens()
        self.sync_database()
        self.send_verifications()

    def sync_database(self):
        self.stdout.write("pulling in new data from wordpress")
        begin, end = get_academic_year()
        props, data = WordPress.get_students_data(as_dict=True, use_cache=False)
        for obj in data:
            try:
                meta = StudentMeta.objects.get(userid=obj['user_id'])

            except StudentMeta.DoesNotExist:
                # assuming that if no meta also no user
                user = User(username=obj['nickname'], first_name=obj['first_name'], last_name=obj['last_name'], email=obj['email'])
                user.save()
                meta = StudentMeta(user=user, userid=obj['user_id'])
            meta.is_student = obj['footloose_student'].lower() == 'yes'
            meta.institute = obj['footloose_institution']
            meta.save()



    def send_verifications(self):
        self.stdout.write("sending verification mails")
        begin, end = get_academic_year()
        usrs = []
        for usr in User.objects.filter(Q(is_staff=False) & Q(studentmeta__is_student=True)):
            if hasattr(usr, "verification"):
                if usr.verification.date < begin:
                    usr.verification.delete()
                else:
                    continue
            if hasattr(usr, "verifytoken"):
                continue
            self.stdout.write("sending mail to {} {}".format(usr.first_name, usr.last_name))
            usrs.append(usr)
        send_student_verification_mail(usrs)


    def clean_tokens(self):
        self.stdout.write("cleaning tokens")
        for token in VerifyToken.objects.all():
            if hasattr(token.user, "verification"):
                token.delete()