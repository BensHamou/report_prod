import django_filters
from django_filters import ChoiceFilter
from django import forms
from .forms import getAttrs
from .models import *
from django.db.models import Q

class ProductFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(unite__icontains=value) |
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
        
class UniteFilter(django_filters.FilterSet):

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
        
class NumoProductFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__icontains=value)
        ).distinct()

    class Meta:
        model = NumoProduct
        fields = ['search']

class TypeStopFilter(django_filters.FilterSet):

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

class ReasonStopFilter(django_filters.FilterSet):

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


class ReportFilter(django_filters.FilterSet):

    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))
    state = ChoiceFilter(choices=Report.STATE_REPORT, widget=forms.Select(attrs=getAttrs('select')), empty_label="État")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(n_lot__icontains=value) | 
            Q(prod_day__icontains=value) | 
            Q(prod_product__designation__icontains=value) | 
            Q(line__designation__icontains=value) | 
            Q(team__designation__icontains=value) | 
            Q(creator__fullname__icontains=value) | 
            Q(site__designation__icontains=value)
        ).distinct()

    class Meta:
        model = Report
        fields = ['search', 'state']
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReportFilter, self).__init__(*args, **kwargs)
        if user:
            if user.role == 'Gestionnaire de stock':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] in 
                                        ['Confirmé', 'Validé par GS', 'Refusé par DI', 'Refusé par GS']]
            elif user.role == 'Directeur Industriel':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] in 
                                        ['Validé par GS', 'Validé par DI',  'Refusé par DI']]
            elif user.role == 'Admin':
                self.filters['state'].field.choices = [choice for choice in self.filters['state'].field.choices if choice[0] not in 
                                        ['Brouillon']]