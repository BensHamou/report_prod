import django_filters
from django_filters import ChoiceFilter, CharFilter, DateFilter, ModelChoiceFilter, FilterSet
from django import forms
from .forms import getAttrs
from .models import *
from django.db.models import Q
from django_filters import DateRangeFilter

class ProductFilter(FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(unite__code__icontains=value) |
            Q(designation__icontains=value) | (
            Q(line__designation__icontains=value) &
            Q(line__in=self.user.lines.all()) )  |
            Q(numo_products__designation__icontains=value)
        ).distinct()

    class Meta:
        model = Product
        fields = ['search']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(ProductFilter, self).__init__(*args, **kwargs)
        
class UniteFilter(FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value) |
            Q(code__icontains=value) |
            Q(conditionnement__icontains=value)
        ).distinct()

    class Meta:
        model = Unite
        fields = ['search']
        
class NumoProductFilter(FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = NumoProduct
        fields = ['search']

class TypeStopFilter(FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value) | (
            Q(line__designation__icontains=value) &
            Q(line__in=self.user.lines.all()) )
        ).distinct()

    class Meta:
        model = TypeStop
        fields = ['search']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(TypeStopFilter, self).__init__(*args, **kwargs)

class ReasonStopFilter(FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value) | (
            Q(type__designation__icontains=value) &
            Q(type__line__in=self.user.lines.all()) )
        ).distinct()

    class Meta:
        model = TypeStop
        fields = ['search']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        self.user = user
        super(ReasonStopFilter, self).__init__(*args, **kwargs)


class ReportFilter(FilterSet):

    other = {'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #f2f2f2; height: 40px; border-radius: 5px;'}
    other_line = {'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #30343b; height: 40px; border-radius: 5px;'}
    search = CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))
    state = ChoiceFilter(choices=Report.STATE_REPORT, widget=forms.Select(attrs=getAttrs('select')), empty_label="État")
    start_date = DateFilter(field_name='prod_day', lookup_expr='gte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    end_date = DateFilter(field_name='prod_day', lookup_expr='lte', widget=forms.widgets.DateInput(attrs= getAttrs('date', other=other), format='%d-%m-%Y'))
    line = ModelChoiceFilter(queryset=Line.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Ligne")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(n_lot__icontains=value) | 
            Q(prod_product__designation__icontains=value) | 
            Q(team__designation__icontains=value) | 
            Q(creator__fullname__icontains=value) | 
            Q(site__designation__icontains=value)
        ).distinct()

    class Meta:
        model = Report
        fields = ['search', 'state', 'start_date', 'end_date', 'line']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReportFilter, self).__init__(*args, **kwargs)
        if user:
            if user.role == 'Gestionnaire de stock':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] in 
                                        ['Confirmé', 'Validé par GS', 'Refusé par DI', 'Refusé par GS', 'Validé par DI']]
            elif user.role == 'Directeur Industriel':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] in 
                                        ['Validé par GS', 'Validé par DI',  'Refusé par DI']]
            elif user.role == 'Nouveau':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] not in 
                                        ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par DI', 'Refusé par GS', 'Refusé par DI', 'Annulé']]
            self.filters['line'].queryset = user.lines.all()

class PlanningFilter(FilterSet):

    other = {'style': 'background-color: rgba(202, 207, 215, 0.5); border-color: transparent; box-shadow: 0 0 6px rgba(0, 0, 0, 0.2); color: #f2f2f2; height: 40px; border-radius: 5px;'}
    line = ModelChoiceFilter(queryset=Line.objects.all(), widget=forms.Select(attrs= getAttrs('select', other=other)), empty_label="Ligne")

