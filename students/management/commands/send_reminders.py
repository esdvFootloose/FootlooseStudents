from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from students.models import VerifyToken
from students.util import send_student_reminders_mail
from django.db.models import Q
from datetime import date

class Command(BaseCommand):
    help = 'send reminder emails with verifytoken'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.clean_tokens()
        self.send_reminders()

    def send_reminders(self):
        usrs = []
        self.stdout.write("sending reminders")
        for usr in User.objects.filter(Q(is_staff=False) & Q(studentmeta__is_student=True)):
            # if it has no verification but has a verify token, this person needs reminding perhaps
            if not hasattr(usr, "verification") and hasattr(usr, "verifytoken"):
                token = usr.verifytoken
                if (date.today() - token.reminded).days >=3:
                    usrs.append(usr)
            if len(usrs) >= 150:
                break
        send_student_reminders_mail(usrs)


    def clean_tokens(self):
        self.stdout.write("cleaning tokens")
        for token in VerifyToken.objects.all():
            if hasattr(token.user, "verification"):
                token.delete()