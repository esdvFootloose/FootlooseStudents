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
        parser.add_argument('--no-sync', dest='no_sync', action='store_true',
                            help='dont sync new members from wordpress, send verifications to already synced members')
        parser.add_argument('--no-send', dest='no_send', action='store_true',
                            help=' dont send verifications yet')
        parser.set_defaults(no_sync=False, only_sync=False)

    def handle(self, *args, **options):
        self.clean_tokens()
        if not options['no_sync']:
            self.sync_database()
        if not options['no_send']:
            self.send_verifications()

    def sync_database(self):
        # TODO: check uniqueness of emails
        self.stdout.write("pulling in new data from wordpress")
        begin, end = get_academic_year()
        props, data = WordPress.get_students_data(as_dict=True, use_cache=False)
        for obj in data:
            try:
                meta = StudentMeta.objects.get(userid=obj['user_id'])
            except StudentMeta.DoesNotExist:
                try:
                    user = User.objects.get(username=obj['nickname'])
                except User.DoesNotExist:
                    user = User(username=obj['nickname'], first_name=obj['first_name'], last_name=obj['last_name'], email=obj['email'])
                    user.save()
                try:
                    meta = user.studentmeta
                except StudentMeta.DoesNotExist:
                    meta = StudentMeta(user=user, userid=obj['user_id'])
            meta.is_student = obj['footloose_student'].lower() == 'yes'
            meta.institute = obj['footloose_institution']
            meta.save()



    def send_verifications(self):
        self.stdout.write("sending verification mails")
        begin, end = get_academic_year()
        usrs = []
        # transip has a limit of 200 emails per 24 hour. when we hit it, there is no way of telling which mail was send and which not
        # so to make sure to keep below the limit never send create a batch larger then 150
        # students who are not in this batch will be processed in the next run
        i = 0
        for usr in User.objects.filter(Q(is_staff=False) & Q(studentmeta__is_student=True)):
            if hasattr(usr, "verification"):
                if usr.verification.date < begin:
                    usr.verification.delete()
                else:
                    continue
            if hasattr(usr, "verifytoken"):
                continue
            if i >= 150:
                break
            self.stdout.write("sending mail to {} {}".format(usr.first_name, usr.last_name))
            usrs.append(usr)
            i += 1
        send_student_verification_mail(usrs)


    def clean_tokens(self):
        self.stdout.write("cleaning tokens")
        for token in VerifyToken.objects.all():
            if hasattr(token.user, "verification"):
                token.delete()