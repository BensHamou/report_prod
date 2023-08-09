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
    
class Product(models.Model):
    UNITE = [
        ('Tn', 'Tn'),
        ('L', 'L'),
    ]

    designation = models.CharField(max_length=100)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, null=True)
    numo_products = models.ManyToManyField(NumoProduct, blank=True)
    unite = models.CharField(max_length=2, choices=UNITE, default='Tn')

    def __str__(self):
        return self.designation
    
class Report(models.Model):
 
    STATE_REPORT = [
        ('Brouillon', 'Brouillon'),
        ('Confirmé', 'Confirmé'),
        ('Validé par GS', 'Validé par GS'),
        ('Validé par DI', 'Validé par DI'),
        ('Refusé par GS', 'RRefusé par GS'),
        ('Refusé par DI', 'Refusé par DI'),
        ('Annulé', 'Annulé'),
    ]

    creator = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Gestionnaire de production'}) ##
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    state = models.CharField(choices=STATE_REPORT, max_length=40)
    prod_product = models.ForeignKey(Product, null=True, on_delete=models.CASCADE, related_name='prod_product') ##
    n_lot = models.CharField(max_length=30)
    line = models.ForeignKey(Line, on_delete=models.CASCADE) ##
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True) ##
    prod_day = models.DateField()
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL) ##
    shift = models.ForeignKey(Horaire, null=True, on_delete=models.SET_NULL)
    used_time =  models.FloatField(default=0, validators=[MinValueValidator(0)])
    nbt_melange = models.FloatField(default=0, validators=[MinValueValidator(0)])
    qte_sac_prod = models.IntegerField(default=1, validators=[MinValueValidator(0)])
    poids_melange = models.FloatField(default=0, validators=[MinValueValidator(0)])
    qte_tn = models.FloatField(default=0, validators=[MinValueValidator(0)])
    qte_sac_reb = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    qte_sac_rec = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    qte_rec = models.FloatField(default=0, validators=[MinValueValidator(0)])
    nbt_pallete = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    gpl_1 = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    gpl_2 = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    observation_rec = models.TextField(null=True)

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

    def __str__(self):
        return self.n_lot + " - " + self.prod_product.designation + " (" + str(self.date_created) +")"

class Arret(models.Model):

    type_stop = models.ForeignKey(TypeStop, null=True, on_delete=models.SET_NULL)
    reason_stop = models.ForeignKey(ReasonStop, null=True, on_delete=models.SET_NULL)
    
    hour = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(12)])
    minutes = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(59)])
    
    @property
    def duration(self):
        return round(self.hour + self.minutes / 60 , 2)
    
    actions = models.TextField()
    observation = models.TextField(null=True)

    report = models.ForeignKey(Report, on_delete=models.CASCADE)

    def __str__(self):
        return self.type_stop.designation + " - " + self.reason_stop.designation + ", a duré " + str(self.duration) + "."

class MPConsumed(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    
    numo_product = models.ForeignKey(NumoProduct, null=True, on_delete=models.CASCADE)
    qte_consumed = models.FloatField(default=0, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True)


    def __str__(self):
        return self.numo_product.designation + " (" + str(self.qte_consumed) +")"
    
class EtatSilo(models.Model):

    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    
    silo = models.ForeignKey(Silo, null=True, on_delete=models.CASCADE)
    etat = models.FloatField(default=0, validators=[MinValueValidator(0)])
    observation = models.TextField(null=True)


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