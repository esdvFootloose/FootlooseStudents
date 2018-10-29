from django.db import models

# Applied Physics
# Biomedical Engineering
# Built Environment
# Chemical Engineering and Chemistry
# Electrical Engineering
# Industrial Design
# Industrial Engineering and Innovation Sciences
# Mathematics and Computer Science
# Mechanical Engineering

class Cursus(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Member(models.Model):
    gender_options = (
        ('F', "Female"),
        ('M', "Male")
    )

    faculty_options = (
        ("TN", "Applied Physics"),
        ("BMT", "Biomedical Engineering"),
        ("BE", "Built Environment"),
        ("ST", "Chemical Engineering and Chemistry"),
        ("ELE", "Electrical Engineering"),
        ("ID", "Industrial Design"),
        ("IE/IS", "Industrial Engineering and Innovation Sciences"),
        ("W&I", "Mathematics and Computer Science"),
        ("WTB", "Mechanical Engineering")
    )

    institute_options = (
        (0, "Eindhoven University of Technology"),
        (1, "Fontys"),
        (2, "Design Academy"),
        (4, "Other"),
        (5, "None")
    )

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    student = models.BooleanField()
    institute = models.IntegerField(choices=institute_options)
    institute_other = models.CharField(max_length=128, null=True, blank=True)
    faculty = models.CharField(max_length=5, choices=faculty_options, null=True, blank=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=1, choices=gender_options)
    subscriptions = models.ManyToManyField(Cursus, related_name='members')

    def load_from_csv(self, props, data):
        self.first_name = data[props.index('first_name')].lower()
        self.last_name = data[props.index('last_name')].lower()
        try:
            self.gender = data[props.index("gender")][0]
        except:
            self.gender = 'M'
        self.birth_date = data[props.index('birth_date')].replace('/', '-')
        self.student = data[props.index('footloose_student')].lower() == 'yes'
        if self.student:
            self.institute = [x[0] for x in self.institute_options if x[1] == data[props.index('footloose_institution')]][0]
            if self.institute == 0:
                self.faculty = [x[0] for x in self.faculty_options if x[1] == data[props.index('footloose_faculty')]][0]
        else:
            self.institute = 5
            self.institute_other = data[props.index('footloose_otherinstitution')]


    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)