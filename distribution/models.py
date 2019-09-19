from django.db import models
from django.contrib.auth.models import User

class CourseType(models.Model):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class Course(models.Model):
    name = models.ForeignKey(CourseType, on_delete=models.PROTECT)
    level = models.IntegerField()
    levelname = models.CharField(max_length=512, null=True, blank=True)
    limit = models.IntegerField(default=24)

    def __str__(self):
        if self.levelname is not None:
            return "{} {}".format(self.name, self.levelname)
        return "{} {}".format(self.name, self.level)

class Couple(models.Model):
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couples_leader')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='couples_follower')

    def __str__(self):
        if self.follower is not None:
            return "{} with {}".format(self.leader, self.follower)
        else:
            return str(self.leader)

class Distribution(models.Model):
    reason_choices = (
        (0, "manual"),
        (1, "active member"),
        (2, "student"),
        (3, "lottery"),
        (4, "else")
    )

    couple = models.ForeignKey(Couple, on_delete=models.PROTECT, related_name='distributions')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='distributions')
    reason = models.IntegerField(choices=reason_choices)

    def __str__(self):
        return "{} for course {} with reason {}".format(self.couple, self.course, self.get_reason_display())
