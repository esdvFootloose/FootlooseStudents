from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    name = models.CharField(max_length=512)
    level = models.IntegerField()
    levelname = models.CharField(max_length=512, null=True, blank=True)
    limit = models.IntegerField(default=24)

    def __str__(self):
        if self.levelname is not None:
            return "{} {}".format(self.name, self.levelname)
        return "{} {}".format(self.name, self.level)