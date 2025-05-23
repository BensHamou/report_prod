from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Horaire(models.Model):
    hour_start = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(23)])
    minutes_start = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(59)])
    hour_end = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(23)])
    minutes_end = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(59)])    
    
    @property
    def passed_time(self):
        total_start = self.hour_start + self.minutes_start / 60 
        total_end = self.hour_end + self.minutes_end / 60 
        total = total_end - total_start
        if total < 0:
            total += + 24
        return round(total, 2)

    @property
    def name(self):
        name = str(self.hour_start) + 'H'
        if self.minutes_start > 0:
            name += str(self.minutes_start) + 'M' 
        name += '-' + str(self.hour_end) + 'H'
        if self.minutes_end > 0:
            name += str(self.minutes_end) + 'M'
        return name

    def __str__(self):
        return self.name
    
class Site(models.Model):
    designation = models.CharField(max_length=100)
    horaires = models.ManyToManyField(Horaire, blank=True)
    address = models.CharField(max_length=250, null=True)

    def __str__(self):
        return self.designation
    
    def lines(self):
        return self.line_set.all()

class Line(models.Model):
    designation = models.CharField(max_length=100)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    obj_ctd = models.FloatField(default=0, null=True, validators=[MinValueValidator(0)])
    prefix_line = models.CharField(max_length=5, blank=True, null=True)
    include_cron = models.BooleanField(default=False)
    allowed_delay = models.IntegerField(default=0, validators=[MinValueValidator(0)]) 
    
    def teams(self):
        return self.team_set.all()
    
    def silos(self):
        return self.silo_set.all()
    
    def shifts(self):
        return self.site.horaires.all()

    def __str__(self):
        return self.designation

class Team(models.Model):
    designation = models.CharField(max_length=50)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)

    def __str__(self):
        return self.designation + ' ('+self.line.designation +')'

class Objectives(models.Model):
    line = models.ForeignKey(Line, on_delete=models.CASCADE)
    date_obj = models.DateField()
    objectif = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.line.designation + ' ' + str(self.date_obj) + ' ('+self.line.designation +')'

class Silo(models.Model):
    designation = models.CharField(max_length=50)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)

    def __str__(self):
        return self.designation
    
class Setting(models.Model):
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self):
        return self.name + ' : ' + self.value

class User(AbstractUser):

    ROLE_CHOICES = [
        ('Nouveau', 'Nouveau'),
        ('Gestionnaire de production', 'Gestionnaire de production'),
        ('Gestionnaire de stock', 'Gestionnaire de stock'),
        ('Maintenancier', 'Maintenancier'),
        ('Observateur', 'Observateur'),
        ('Admin', 'Admin'),
    ]

    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    fullname = models.CharField(max_length=255)
    role = models.CharField(choices=ROLE_CHOICES, max_length=30)
    lines = models.ManyToManyField(Line, blank=True, related_name='users')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    is_admin = models.BooleanField(default=False)
    do_notify = models.BooleanField(default=False)
    lines_to_notify = models.ManyToManyField(Line, blank=True, related_name='users_to_notify')

    fields = ('username', 'fullname', 'email', 'role', 'lines', 'is_admin', 'do_notify', 'lines_to_notify', 'first_name', 'last_name')

    
    def __str__(self):
        return self.fullname

    class Meta(AbstractUser.Meta):
       swappable = 'AUTH_USER_MODEL'