import django_filters
from django import forms
from django.db.models import Q

from .models import *
from report.forms import getAttrs

class UserFilter(django_filters.FilterSet):
    
    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(fullname__icontains=value) |
            Q(username__icontains=value) |
            Q(role__icontains=value) |
            Q(lines__designation__contains=value)
        ).distinct()

    class Meta:
        model = User
        fields = ['search']

class SiteFilter(django_filters.FilterSet):
    
    search = django_filters.CharFilter(method='filter_search', widget=forms.TextInput(attrs=getAttrs('search', 'Rechercher..')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(designation__contains=value) |
            Q(line__designation__contains=value)|
            Q(line__team__designation__contains=value)
        ).distinct()

    class Meta:
        model = Site
        fields = ['search']
