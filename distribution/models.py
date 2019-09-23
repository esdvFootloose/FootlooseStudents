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
    coupledance = models.BooleanField(default=False)

    def __str__(self):
        if self.levelname is not None:
            return "{} {}".format(self.name, self.levelname)
        return "{} {}".format(self.name, self.level)

    def get_machine_name(self):
        return  self.__str__().replace(' ', '_')

    def get_couples(self):
        return self.distributions.filter(admitted=True).order_by('couple')

class Couple(models.Model):
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='couples_leader')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True,
                                 related_name='couples_follower')

    def get_highest_status(self):
        if self.leader.studentmeta.is_activemember:
            return "active_member"
        if self.leader.studentmeta.is_student:
            if hasattr(self.leader, 'verifytoken') or hasattr(self.leader, 'verifytoken'):
                return "student_eindhoven"
            else:
                return "student"

        if self.follower is not None:
            if self.follower.studentmeta.is_activemember:
                return "active_member"
            if self.follower.studentmeta.is_student:
                if hasattr(self.follower, 'verifytoken') or hasattr(self.follower, 'verifytoken'):
                    return "student_eindhoven"
                else:
                    return "student"

        return None

    def __str__(self):
        if self.follower is not None:
            return "{} with {}".format(self.leader, self.follower)
        else:
            return str(self.leader)

    def get_admitted_courses(self):
        return self.distributions.filter(admitted=True).order_by('course')

class Distribution(models.Model):
    reason_choices = (
        (0, "manual"),
        (1, "automatic"),
    )

    couple = models.ForeignKey(Couple, on_delete=models.PROTECT, related_name='distributions')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='distributions')
    reason = models.IntegerField(choices=reason_choices)
    admitted = models.BooleanField(default=False)

    def __str__(self):
        return "{} for course {} with reason {}".format(self.couple, self.course, self.get_reason_display())
