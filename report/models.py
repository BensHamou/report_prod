from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import *


class TypeStop(models.Model):

    designation = models.CharField(max_length=100)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    
    def arrets(self):
        return self.arret_set.all()

    def reasonStops(self):
        return self.reasonstop_set.all()

    def __str__(self):
        return self.designation 

class ReasonStop(models.Model):

    designation = models.CharField(max_length=100)

    type = models.ForeignKey(TypeStop, on_delete=models.CASCADE, null=True)

    def arrets(self):
        return self.arret_set.all()

    def __str__(self):
        return self.designation

class NumoProduct(models.Model):

    designation = models.CharField(max_length=100)

    def __str__(self):
        return self.designation

class Unite(models.Model):

    code = models.CharField(max_length=20)
    designation = models.CharField(max_length=20)
    conditionnement = models.CharField(max_length=20)

    def __str__(self):
        return self.code
    
class Product(models.Model):

    designation = models.CharField(max_length=100)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    numo_products = models.ManyToManyField(NumoProduct, blank=True)
    unite = models.ForeignKey(Unite, on_delete=models.SET_NULL, null=True, blank=True)
    qte_per_container = models.FloatField(default=0, null=True, validators=[MinValueValidator(0)])
    poids_melange = models.FloatField(default=0, null=True, blank=True, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.designation
    
class Report(models.Model):
 
    STATE_REPORT = [
        ('Brouillon', 'Brouillon'),
        ('Confirmé', 'Confirmé'),
        ('Validé par GS', 'Validé par GS'),
        ('Validé par DI', 'Validé par DI'),
        ('Refusé par GS', 'Refusé par GS'),
        ('Refusé par DI', 'Refusé par DI'),
        ('Annulé', 'Annulé'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Gestionnaire de production'}) ##
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_REPORT, max_length=40)
    prod_product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='prod_product') ##
    n_lot = models.IntegerField()
    line = models.ForeignKey(Line, on_delete=models.CASCADE) ##
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True) ##
    prod_day = models.DateField()
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL) ##
    shift = models.ForeignKey(Horaire, null=True, on_delete=models.SET_NULL)
    used_time =  models.FloatField(default=0, validators=[MinValueValidator(0)])
    nbt_melange = models.FloatField(default=0, validators=[MinValueValidator(0)])
    qte_sac_prod = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    poids_melange = models.FloatField(default=0, validators=[MinValueValidator(0)])
    qte_tn = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])
    qte_sac_reb = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    qte_sac_rec = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    qte_rec = models.FloatField(default=0, validators=[MinValueValidator(0)])
    nbt_pallete = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    gpl_1 = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    gpl_2 = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    observation_rec = models.TextField(null=True, blank=True)

    def mpconsumeds(self):
        return self.mpconsumed_set.all()
    
    def arrets(self):
        return self.arret_set.all()
    
    def etatsilos(self):
        return self.etatsilo_set.all()
    
    def validations(self):
        return self.validation_set.all()
    
    @property
    def total_arrets(self):
        return round(sum(arret.duration for arret in self.arrets()), 2)
    
    @property
    def total_consumed(self):
        return round(sum(c.qte_consumed for c in self.mpconsumeds()), 2)
    
    def __str__(self):
        return str(self.n_lot) + " - " + self.prod_product.designation + " (" + str(self.date_created) +")"

class Arret(models.Model):

    type_stop = models.ForeignKey(TypeStop, null=True, on_delete=models.SET_NULL)
    reason_stop = models.ForeignKey(ReasonStop, null=True, on_delete=models.SET_NULL)
    
    hour = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minutes = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(59)])
    
    @property
    def duration(self):
        return round(self.hour + self.minutes / 60 , 2)
    
    actions = models.TextField(null=True, blank=True)
    observation = models.TextField(null=True, blank=True)

    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return self.type_stop.designation + " - " + self.reason_stop.designation + ", a duré " + str(self.duration) + "."

class MPConsumed(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    
    numo_product = models.ForeignKey(NumoProduct, null=True, on_delete=models.CASCADE)
    qte_consumed = models.FloatField(default=0, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.numo_product.designation + " (" + str(self.qte_consumed) +")"
    
class EtatSilo(models.Model):

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    
    silo = models.ForeignKey(Silo, null=True, on_delete=models.CASCADE)
    etat = models.FloatField(default=0, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.silo.designation + " (" + str(self.etat) +")"
    
class Validation(models.Model):

    STATE_REPORT = [
        ('Brouillon', 'Brouillon'),
        ('Confirmé', 'Confirmé'),
        ('Validé par GS', 'Validé par GS'),
        ('Validé par DI', 'Validé par DI'),
        ('Refusé par GS', 'Refusé par GS'),
        ('Refusé par DI', 'Refusé par DI'),
        ('Annulé', 'Annulé'),
    ]

    old_state = models.CharField(choices=STATE_REPORT, max_length=40)
    new_state = models.CharField(choices=STATE_REPORT, max_length=40)
    date = models.DateTimeField(auto_now_add=True) 
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    refusal_reason = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return "Validation - " + str(self.report.id) + " - " + str(self.date)
    
class Planning(models.Model):

    creator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': ['Directeur Industriel', 'Admin']})
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name='plannings')

    @property
    def shifts_str(self):
        shifts = [str(plan.shift) for plan in self.plans.all()]
        return " & ".join(shifts)

    @property
    def shifts(self):
        return [plan.shift for plan in self.plans.all()]

    class Meta:
        verbose_name = "Planning"
        verbose_name_plural = "Plannings"
        ordering = ['-date_created']
    
    def __str__(self):
        return f"Planning de {self.line} - {self.date_created}"

class Plan(models.Model):

    planning = models.ForeignKey(Planning, on_delete=models.CASCADE, related_name='plans')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    shift = models.ForeignKey(Horaire, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Plans"
        unique_together = ('planning', 'shift')

    def __str__(self):
        return f"{self.planning} - {self.shift}"

class PlanLine(models.Model):

    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_lines')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date = models.DateField()
    products = models.ManyToManyField(Product)

    class Meta:
        verbose_name = "Plan Line"
        verbose_name_plural = "Plan Lines"
        unique_together = ('plan', 'date')
        ordering = ['date']

    def __str__(self):
        return f"{self.plan} - {self.date}"
    