from django.forms import ModelForm, inlineformset_factory
from django import forms
from .models import *
from django.utils import timezone

def getAttrs(type, placeholder='', other={}):
    ATTRIBUTES = {
        'control': {'class': 'form-control', 'style': 'background-color: #cacfd7;', 'placeholder': ''},
        'search': {'class': 'form-control form-input', 'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #f2f2f2; height: 40px; text-indent: 33px; border-radius: 5px;', 'type': 'search', 'placeholder': '', 'id': 'search'},
        'select': {'class': 'form-select', 'style': 'background-color: #cacfd7;'},
        'date': {'type': 'date', 'class': 'form-control dateinput','style': 'background-color: #cacfd7;'},
        'textarea': {"rows": "3", 'style': 'width: 100%', 'class': 'form-control', 'placeholder': '', 'style': 'background-color: #cacfd7;'}
    }

    
    if type in ATTRIBUTES:
        attributes = ATTRIBUTES[type]
        if 'placeholder' in attributes:
            attributes['placeholder'] = placeholder
        if other:
            attributes.update(other)
        return attributes
    else:
        return {}

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['designation', 'line', 'numo_products', 'unite', 'qte_per_container']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    line = forms.ModelChoiceField(queryset=Line.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Ligne")

    numo_products = forms.SelectMultiple(attrs={'class': 'form-select'})
    unite = forms.ModelChoiceField(queryset=Unite.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Unité")
    qte_per_container = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Qté par Sac/Bidon')))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['line'].queryset = user.lines.all()

class NumoProductForm(ModelForm):
    class Meta:
        model = NumoProduct
        fields = ['designation']

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))

class UniteForm(ModelForm):
    class Meta:
        model = Unite
        fields = ['code','designation', 'conditionnement']

    code = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Code')))
    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    conditionnement = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Conditionnement')))

class TypeStopForm(ModelForm):
    class Meta:
        model = TypeStop
        fields = '__all__'

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    line = forms.ModelChoiceField(queryset=Line.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Ligne")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TypeStopForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['line'].queryset = user.lines.all()

class ReasonStopForm(ModelForm):
    class Meta:
        model = ReasonStop
        fields = '__all__'

    designation = forms.CharField(widget=forms.TextInput(attrs=getAttrs('control','Designation')))
    type = forms.ModelChoiceField(queryset=TypeStop.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Type")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReasonStopForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['type'].queryset = TypeStop.objects.filter(line__in=user.lines.all())

class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ['n_lot', 'line', 'site', 'prod_day', 'shift', 'used_time', 'team', 'prod_product', 'qte_sac_prod', 'nbt_melange', 'qte_tn', 'poids_melange' ,'qte_sac_reb', 
                  'qte_sac_rec', 'qte_rec', 'nbt_pallete', 'observation_rec','gpl_1', 'gpl_2']
                

    n_lot = forms.CharField(widget=forms.TextInput(attrs= getAttrs('control','N° Lot')))
    line = forms.ModelChoiceField(queryset=Line.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Ligne")
    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Site")
    prod_day = forms.DateField(initial=timezone.now().date(), widget=forms.widgets.DateInput(attrs= getAttrs('date'), format='%Y-%m-%d'))
    shift = forms.ModelChoiceField(queryset=Horaire.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Horaire")
    used_time = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Temps utilisé')))    
    team = forms.ModelChoiceField(queryset=Team.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Équipe")
    prod_product = forms.ModelChoiceField(queryset=Product.objects.all(), widget=forms.Select(attrs= getAttrs('select')), empty_label="Produit")
    qte_sac_prod = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','Nombre Sacs/Bidons Produit')))
    nbt_melange = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Nombre Mélange')))    
    qte_tn = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Quantité Tn/L', {'max': '200', 'step': '0.01'})))
    qte_sac_reb = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','Nombre Sacs Rebutés')))
    poids_melange = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Poids Mélange')))
    qte_sac_rec = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','Nombre Sacs Récyclés')))
    qte_rec = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Quantité Recyclée')))
    nbt_pallete = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','Nombre Palletes')))
    gpl_1 = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','% Citerne GPL 1')))
    gpl_2 = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','% Citerne GPL 2')))
    observation_rec = forms.CharField(widget=forms.Textarea(attrs= getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        lines = kwargs.pop('lines', None)
        teams = kwargs.pop('teams', None)
        team = kwargs.pop('team', None)
        site = kwargs.pop('site', None)
        DI = kwargs.pop('DI', None)
        state = kwargs.pop('state', None)
        products = kwargs.pop('products', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        if lines is not None:
            self.fields['line'].queryset = lines
            self.fields['team'].queryset = teams
            #self.fields['site'].queryset = Site.objects.filter(id = site.id)
            self.fields['line'].initial = lines.first()
            self.fields['team'].initial = team
            self.fields['qte_tn'].initial = 0
            self.fields['site'].initial = site
            self.fields['prod_product'].queryset = products
            if not admin and len(lines) < 2:
                self.fields['line'].widget.attrs['disabled'] = True
            if not admin:    
                self.fields['team'].widget.attrs['disabled'] = True
                self.fields['site'].widget.attrs['disabled'] = True
                self.fields['qte_tn'].widget.attrs['disabled'] = True
            
            if DI and state == 'Validé par GS':
                fields_to_disable = ['line', 'n_lot', 'prod_day', 'shift', 'used_time', 'team', 'prod_product', 'qte_sac_prod', 'nbt_melange',
                                     'qte_sac_reb', 'poids_melange', 'qte_sac_rec', 'qte_rec', 'nbt_pallete', 'gpl_1', 'gpl_2', 'observation_rec']
                for field_name in fields_to_disable:
                    self.fields[field_name].widget.attrs['disabled'] = True


class MPConsumedForm(ModelForm):
    class Meta:
        model = MPConsumed
        fields = '__all__'

    numo_product = forms.ModelChoiceField(queryset=NumoProduct.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Numo Product")
    qte_consumed = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','Qte Consomée')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        state = kwargs.pop('state', None)
        super(MPConsumedForm, self).__init__(*args, **kwargs)
        if user:
            if not user.role == 'Admin':
                self.fields['numo_product'].widget.attrs['disabled'] = True
            if user.role == 'Directeur Industriel' and state == 'Validé par GS':
                self.fields['qte_consumed'].widget.attrs['disabled'] = True
                self.fields['observation'].widget.attrs['disabled'] = True

class EtatSiloForm(ModelForm):
    class Meta:
        model = EtatSilo
        fields = '__all__'

    silo = forms.ModelChoiceField(queryset=Silo.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Silo")
    etat = forms.FloatField(widget=forms.NumberInput(attrs= getAttrs('control','État')))
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        role = kwargs.pop('role', None)
        state = kwargs.pop('state', None)
        super(EtatSiloForm, self).__init__(*args, **kwargs)
        self.fields['silo'].widget.attrs['disabled'] = True
        if role == 'Directeur Industriel' and state == 'Validé par GS':
            self.fields['etat'].widget.attrs['disabled'] = True
            self.fields['observation'].widget.attrs['disabled'] = True



class ArretForm(ModelForm):
    class Meta:
        model = Arret
        fields = ['type_stop', 'reason_stop', 'hour', 'minutes', 'actions', 'observation']
    
    type_stop = forms.ModelChoiceField(queryset=TypeStop.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Type")
    reason_stop = forms.ModelChoiceField(queryset=ReasonStop.objects.all(), widget=forms.Select(attrs=getAttrs('select')), empty_label="Raison")
    hour = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','H')))
    minutes = forms.IntegerField(widget=forms.NumberInput(attrs= getAttrs('control','M')))
    actions = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Actions')), required=False)
    observation = forms.CharField(widget=forms.Textarea(attrs=getAttrs('textarea','Observation')), required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance')
        super(ArretForm, self).__init__(*args, **kwargs)
        if user: 
            types = TypeStop.objects.filter(line__in=user.lines.all())
            self.fields['type_stop'].queryset = types
            self.fields['reason_stop'].queryset = ReasonStop.objects.filter(type__in=types)
        self.fields['type_stop'].required = True
        self.fields['reason_stop'].required = True
        if instance:
            self.fields['reason_stop'].queryset = ReasonStop.objects.filter(type=instance.type_stop.id)

MPConsumedsFormSet = inlineformset_factory(Report, MPConsumed, form=MPConsumedForm, fields=['numo_product', 'qte_consumed', 'observation'], extra=0)

EtatSiloFormSet = inlineformset_factory(Report, EtatSilo, form=EtatSiloForm, fields=['silo', 'etat', 'observation'], extra=0)

ArretsFormSet = inlineformset_factory(Report, Arret, form=ArretForm,fields=['type_stop', 'reason_stop', 'hour', 'minutes', 'actions', 'observation'], 
    can_delete=True, can_delete_extra=True, extra=0)