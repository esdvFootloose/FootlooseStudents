from django.core.management.base import BaseCommand
from distribution.models import Course, CourseType


class Command(BaseCommand):
    help = 'initialize the database with necesarry objects'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        self.init_populate()

    def init_populate(self):
        self.stdout.write("Generating course objects")
        courses = [
            ("ballet", 3, False),
            ("modern", 3, False),
            ("hiphop", 3, False),
            ("zouk", 3, True),
            ("salsa", 4, True),
            ("ballroom", 5, True),
        ]

        names = {
            "ballroom" : [
                "bronze",
                "silver",
                "silverstar",
                "gold",
                "topclass"
            ]
        }

        for c in courses:
            ctype = CourseType(name=c[0])
            ctype.save()
            for i in range(c[1]):
                obj = Course(name=ctype,level=i+1, coupledance=c[2])
                if c[0] in names:
                    obj.levelname = names[c[0]][i]
                obj.save()

        Course(name=CourseType.objects.get(name='hiphop'), level=4, levelname='demoteam').save()
