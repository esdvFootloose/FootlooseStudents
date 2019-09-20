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
            ("ballet", 3),
            ("modern", 3),
            ("hiphop", 3),
            ("zouk", 3),
            ("salsa", 4),
            ("ballroom", 5),
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
                obj = Course(name=ctype,level=i+1)
                if c[0] in names:
                    obj.levelname = names[c[0]][i]
                obj.save()
