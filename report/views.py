from .models import *
from account.models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from account.views import admin_required, DI_GS_required
import uuid
from .forms import *
from .filters import *
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.db.models import Count
from django.template.defaulttags import register
from functools import wraps
from django.core.mail import send_mail
from django.utils.html import format_html
from datetime import datetime
from account.models import Horaire
from django import forms
from django.forms import formset_factory
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import locale
from account.views import admin_or_di_required

def check_creator(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        report_id = kwargs.get('pk')
        report = Report.objects.get(id=report_id)
        if (report.creator != request.user or request.user.role != "Gestionnaire de production") and request.user.role != 'Admin':
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

def check_creatorArret(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        arret_id = kwargs.get('pk')
        arret = Arret.objects.get(id=arret_id)
        if arret.report.state == 'Validé par GS' and request.user.role == 'Directeur Industriel':
            return view_func(request, *args, **kwargs)
        if request.user.role == 'Admin':
            return view_func(request, *args, **kwargs)
        if not (arret.report.state in ['Brouillon','Refusé par GS', 'Refusé par DI'] and 
                (request.user.role == "Gestionnaire de production" and request.user == arret.report.creator)):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key,0)

@register.filter
def startwith(value, word):
    return str(value).startswith(word)

@register.filter
def is_login(messages):
    for message in messages:
        if str(message).startswith('LOGIN : '):
            return True
    return False

@register.filter
def loginerror(value, word):
    return str(value)[len(word):]

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, "")
    return ""

# PRODUCTS
@login_required(login_url='login')
@admin_required 
def listProductList(request):
    products = Product.objects.filter(line__in=request.user.lines.all()).order_by('id')
    filteredData = ProductFilter(request.GET, queryset=products, user = request.user)
    products = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(products, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_products.html', context)

@login_required(login_url='login')
@admin_required
def deleteProductView(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('products')

    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createProductView(request):
    form = ProductForm(user = request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('products')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form, 'selectedNumos': []}
    return render(request, 'product_form.html', context)

@login_required(login_url='login')
@admin_required
def editProductView(request, id):
    product = Product.objects.get(id=id)

    selectedNumos = []

    for numo in product.numo_products.all():
        selectedNumos.append(numo.id)

    form = ProductForm(instance=product, user = request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product, user = request.user)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('products')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'product': product, 'selectedNumos': selectedNumos}

    return render(request, 'product_form.html', context)

# NUMO PRODUCTS
@login_required(login_url='login')
@admin_required
def listNumoProductView(request):
    products = NumoProduct.objects.all().order_by('id')
    filteredData = NumoProductFilter(request.GET, queryset=products)
    products = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(products, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_numo_products.html', context)

@login_required(login_url='login')
@admin_required
def deleteNumoProductView(request, id):
    numoProduct = NumoProduct.objects.get(id=id)
    numoProduct.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('numo_products')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createNumoProductView(request):
    form = NumoProductForm()
    if request.method == 'POST':
        form = NumoProductForm(request.POST)
        if form.is_valid():
            designation = form.cleaned_data['designation']
            numoProduct = NumoProduct(designation=designation)
            numoProduct.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('numo_products')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'numo_product_form.html', context)

@login_required(login_url='login')
@admin_required
def editNumoProductView(request, id):
    numoProduct = NumoProduct.objects.get(id=id)
    form = NumoProductForm(instance=numoProduct)
    if request.method == 'POST':
        form = NumoProductForm(request.POST, instance=numoProduct)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('numo_products')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)
    context = {'form': form, 'numoProduct': numoProduct}

    return render(request, 'numo_product_form.html', context)

# STOPPING TYPE
@login_required(login_url='login')
@admin_required
def listTypeStopList(request):
    types = TypeStop.objects.filter(line__in=request.user.lines.all()).order_by('id')
    filteredData = TypeStopFilter(request.GET, queryset=types, user = request.user)
    
    types = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(types, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_types.html', context)

@login_required(login_url='login')
@admin_required
def deleteTypeStopView(request, id):
    types = TypeStop.objects.get(id=id)
    types.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('types')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createTypeStopView(request):
    form = TypeStopForm(user = request.user)
    if request.method == 'POST':
        form = TypeStopForm(request.POST)
        if form.is_valid():
            designation = form.cleaned_data['designation']
            line = form.cleaned_data['line']
            type = TypeStop(designation=designation, line=line)
            type.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('types')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}

    return render(request, 'type_form.html', context)

@login_required(login_url='login')
@admin_required
def editTypeStopView(request, id):
    type = TypeStop.objects.get(id=id)
    form = TypeStopForm(instance=type, user = request.user)

    if request.method == 'POST':
        form = TypeStopForm(request.POST, instance=type)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('types')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'
            return redirect(redirect_url)

    context = {'form': form, 'type': type}

    return render(request, 'type_form.html', context)

# STOPPING REASONS
@login_required(login_url='login')
@admin_required
def listReasonStopList(request):
    reasons = ReasonStop.objects.filter(type__in=TypeStop.objects.filter(line__in=request.user.lines.all())).order_by('id')
    filteredData = ReasonStopFilter(request.GET, queryset=reasons, user = request.user)
    reasons = filteredData.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12   
    paginator = Paginator(reasons, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData, 
    }
    return render(request, 'list_reasons.html', context)

@login_required(login_url='login')
@admin_required
def deleteReasonStopView(request, id):
    reason = ReasonStop.objects.get(id=id)
    reason.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('reasons')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createReasonStopView(request):
    form = ReasonStopForm(user = request.user)
    if request.method == 'POST':
        form = ReasonStopForm(request.POST)
        if form.is_valid():
            designation = form.cleaned_data['designation']
            type = form.cleaned_data['type']
            reason = ReasonStop(designation=designation, type=type)
            reason.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reasons')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}

    return render(request, 'reason_form.html', context)

@login_required(login_url='login')
@admin_required
def editReasonStopView(request, id):
    reason = ReasonStop.objects.get(id=id)
    form = ReasonStopForm(instance=reason, user = request.user)

    if request.method == 'POST':
        form = ReasonStopForm(request.POST, instance=reason, user = request.user)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('reasons')
            page = request.GET.get('page', '1')
            page_size = request.GET.get('page_size', '12')
            search = request.GET.get('search', '')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}&page_size={page_size}&search={search}'

            return redirect(redirect_url)

    context = {'form': form, 'reason': reason}

    return render(request, 'reason_form.html', context)

#REPORTS

class CheckEditorMixin:
    def check_editor(self, report):
        if self.request.user.role == 'Directeur Industriel' and report.state == 'Validé par GS':
            return True
        if (report.creator != self.request.user or self.request.user.role != "Gestionnaire de production" or 
            report.state not in ['Brouillon','Refusé par GS','Refusé par DI']) and self.request.user.role != 'Admin':
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_editor(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckCreatorMixin:
    def check_can_create(self):
        if self.request.user.role in ['Observateur', 'Nouveau']:
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        if not self.check_can_create():
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)    
    
class CheckNoRefusedMixin:
    def check_has_refused(self):
        lines = self.request.user.lines.all()
        reports = Report.objects.filter(Q(creator=self.request.user), Q(line__in=lines) & Q(state='Refusé par GS') | Q(state='Refusé par DI'))
        return len(reports) == 0

    def dispatch(self, request, *args, **kwargs):
        if not self.check_has_refused():
            return render(request, '403_refusal.html', status=403)
        return super().dispatch(request, *args, **kwargs)
    
class CheckReportViewerMixin:
    def check_viewer(self, report):
        lines = self.request.user.lines.all()
        if report.line not in lines and self.request.user.role != 'Admin':
            return False
        return True

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  
        if not self.check_viewer(report):
            return render(request, '403.html', status=403)
        return super().dispatch(request, *args, **kwargs)

class ReportInline():
    form_class = ReportForm
    model = Report
    template_name = "report_form.html"    
    login_url = 'login'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['admin'] = self.request.user.role == 'Admin'
        kwargs['DI'] = self.request.user.role == 'Directeur Industriel'
        kwargs['lines'] = self.request.user.lines.all()
        kwargs['team'] = self.request.user.team
        kwargs['site'] = self.request.user.lines.all().first().site
        kwargs['teams'] = Team.objects.filter(line__in=self.request.user.lines.all())
        kwargs['products'] = Product.objects.filter(line__in=self.request.user.lines.all())
        if self.object:
            kwargs['state'] = self.object.state
        return kwargs

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        
        report = form.save(commit=False) 
        if not report.state or report.state == 'Brouillon':
            report.state = 'Brouillon'
        
        if not report.id:
            report.creator = self.request.user
        
        report.save()

        new = True
        if self.object:
            new = False
        else:
            self.object = report

        for name, formset in named_formsets.items():
            formset_save_func = getattr(self, 'formset_{0}_valid'.format(name), None)
            if formset_save_func is not None:
                formset_save_func(formset)
            else:
                formset.save()

        if not new:
            cache_param = str(uuid.uuid4())
            url_path = reverse('report_detail', args=[self.object.pk])
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
        return redirect('list_report')

    def formset_arrets_valid(self, formset):
        arrets = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for arret in arrets:
            arret.report = self.object
            arret.save()

    def formset_etatsilos_valid(self, formset):
        etatsilos = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for silo in etatsilos:
            silo.report = self.object
            silo.save()

    def formset_consumed_products_valid(self, formset):
        consumed_products = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for consumed_product in consumed_products:
            consumed_product.report = self.object
            consumed_product.save()


class ReportCreate(LoginRequiredMixin, CheckCreatorMixin, CheckNoRefusedMixin, ReportInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'arrets': ArretsFormSet(prefix='arrets', form_kwargs={'user': self.request.user}),
                'consumed_products': MPConsumedsFormSet(prefix='consumed_products', form_kwargs={'user': self.request.user}),
                'etatsilos': EtatSiloFormSet(prefix='etatsilos'),
            }
        else:
            return {
                'arrets': ArretsFormSet(self.request.POST or None, prefix='arrets', form_kwargs={'user': self.request.user}),
                'consumed_products': MPConsumedsFormSet(self.request.POST or None, prefix='consumed_products', form_kwargs={'user': self.request.user}),
                'etatsilos': EtatSiloFormSet(self.request.POST or None, prefix='etatsilos'),
            }

class ReportUpdate(LoginRequiredMixin, CheckEditorMixin, ReportInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'arrets': ArretsFormSet(self.request.POST or None, instance=self.object, prefix='arrets', form_kwargs={'user': self.request.user}),
            'consumed_products': MPConsumedsFormSet(self.request.POST or None, instance=self.object, prefix='consumed_products', form_kwargs={'user': self.request.user, 'state': self.object.state}),
            'etatsilos': EtatSiloFormSet(self.request.POST or None, instance=self.object, prefix='etatsilos', form_kwargs={'role': self.request.user.role, 'state': self.object.state }),
        }
    
class ReportDetail(LoginRequiredMixin, CheckReportViewerMixin, DetailView):
    model = Report
    template_name = 'report_detail.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [field for field in self.model._meta.get_fields() if field.concrete]
        context['fields'] = fields
        return context

class ReportList(LoginRequiredMixin, FilterView):
    model = Report
    template_name = "list_reports.html"
    context_object_name = "reports"
    filterset_class = ReportFilter
    ordering = ['-prod_day']
        
    all_GP = ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par DI', 'Refusé par GS', 'Refusé par DI', 'Annulé']
    all_A = ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par DI', 'Refusé par GS', 'Refusé par DI', 'Annulé']
    all_GS = ['Confirmé', 'Validé par GS', 'Refusé par GS', 'Refusé par DI', 'Validé par DI']
    all_DI = ['Validé par GS', 'Validé par DI', 'Refusé par DI']
    all_NV = ['']

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.user.role
        lines = self.request.user.lines.all()

        if role == 'Gestionnaire de production':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_GP))

        elif role == 'Gestionnaire de stock':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_GS))
                
        elif role == 'Directeur Industriel':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_DI))
                
        elif role == 'Nouveau':
            queryset = queryset.filter(Q(state__in=self.all_NV))

        elif role in ['Admin', 'Observateur']:
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_A))

        return queryset    
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_size_param = self.request.GET.get('page_size')
        page_size = int(page_size_param) if page_size_param else 12        
        paginator = Paginator(context['reports'], page_size)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page'] = page_obj
        context['state_totals'] = self.get_state_totals()
        context['all_total'] = len(context['reports'])
        role_state = {'Gestionnaire de production': self.all_GP, 'Gestionnaire de stock': self.all_GS, 'Directeur Industriel': self.all_DI, 'Admin': self.all_A, 'Observateur': self.all_A, 'Nouveau': self.all_NV}
        context['role_state'] = role_state
        return context
    
    def get_state_totals(self):
        user = self.request.user
        line_condition = Q(line__in=user.lines.all())

        if user.role == 'Gestionnaire de production':
            creator_condition = Q(creator=user)
        else:
            creator_condition = Q()

        state_totals = (
            Report.objects.filter(creator_condition | line_condition)
            .values('state')
            .annotate(total=Count('state'))
            .order_by('state')
        )

        return {state['state']: state['total'] for state in state_totals}


@login_required(login_url='login')
@check_creator
def delete_report(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Le rapport n\'existe pas'
            )
        url_path = reverse('list_report')
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    report.delete()
    messages.success(
            request, 'Rapport supprimé avec succès'
            )
    url_path = reverse('list_report')
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@check_creatorArret
def delete_arret(request, pk):
    try:
        arret = Arret.objects.get(id=pk)
    except Arret.DoesNotExist:
        messages.success(
            request, 'L\'arrêt n\'existe pas'
            )
        url_path = reverse('update_report', args=[arret.report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    arret.delete()
    messages.success(
            request, 'Arrêt supprimé avec succès'
            )
    url_path = reverse('update_report', args=[arret.report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
def get_data_by_line(request):
    line_id = request.GET.get('line_id')
    if line_id == '':
        return JsonResponse({'type_stops': [], 'reason_stops': [] })
    
    type_stops = TypeStop.objects.filter(line_id=line_id)
    line = Line.objects.get(pk=line_id)

    horaires_list = [{'id': horaire.id, 'designation': horaire.__str__()} for horaire in line.site.horaires.all()]
    silo_list = [ silo.id for silo in Silo.objects.filter(line_id=line_id)]
    team_list = [{'id': team.id, 'designation': team.__str__()} for team in Team.objects.filter(line_id=line_id)]
    product_list = [{'id': product.id, 'designation': product.__str__()} for product in Product.objects.filter(line_id=line_id)]
    type_stop_list = [{'id': type_stop.id, 'designation': type_stop.__str__()} for type_stop in type_stops]
    reason_stop_list = [{'id': reason_stop.id, 'designation': reason_stop.__str__()} for reason_stop in ReasonStop.objects.none()]

    return JsonResponse({'teams': team_list, 'products': product_list, 'type_stops': type_stop_list, 
                         'reason_stops': reason_stop_list, 'silos': silo_list, 'horaires_list': horaires_list})

@login_required(login_url='login')
def get_arretData_by_line(request):
    line_id = request.GET.get('line_id')
    if line_id == '':
        return JsonResponse({'type_stops': [], 'reason_stops': [] })
    type_stops = TypeStop.objects.filter(line_id=line_id)

    type_stop_list = [{'id': type_stop.id, 'designation': type_stop.__str__()} for type_stop in type_stops]
    reason_stop_list = [{'id': reason_stop.id, 'designation': reason_stop.__str__()} for reason_stop in ReasonStop.objects.none()]

    return JsonResponse({'type_stops': type_stop_list, 'reason_stops': reason_stop_list })

@login_required(login_url='login')
def get_reasons_by_type(request):
    if request.GET.get('type_id') == '':
        return JsonResponse({'reason_stops': [] })
    return JsonResponse({'reason_stops': [{'id': reason_stop.id, 'designation': reason_stop.__str__()} 
                                          for reason_stop in ReasonStop.objects.filter(type_id=request.GET.get('type_id'))] })

@login_required(login_url='login')
def get_numo_by_product(request):
    numo_products = NumoProduct.objects.filter(product=request.GET.get('product'))
    try:
        product = Product.objects.get(id=request.GET.get('product'))
        qte_per_container = product.qte_per_container
        code_unite = product.unite.code
        poids_melange = product.poids_melange
    except Product.DoesNotExist:
        qte_per_container = 0

    mp_list = [numo_product.id for numo_product in numo_products]

    return JsonResponse({'mp_list': mp_list, 'qte_per_container': qte_per_container, 'code_unite': code_unite, 'poids_melange': poids_melange})

@login_required(login_url='login')
def get_shift_max(request):
    try:
        max_by_shift = Horaire.objects.get(id=request.GET.get('idShift')).passed_time
    except Product.DoesNotExist:
        max_by_shift = 0

    return JsonResponse({'max_by_shift': max_by_shift })

@login_required(login_url='login')
def get_qte_per_container(request):
    try:
        product = Product.objects.get(id=request.GET.get('product'))
        qte_per_container = product.qte_per_container
        code_unite = product.unite.code
    except Product.DoesNotExist:
        qte_per_container = 0
    return JsonResponse({'qte_per_container': qte_per_container, 'code_unite': code_unite })

@login_required(login_url='login')
@check_creator
def confirmReport(request, pk):

    params = {
        'page': request.GET.get('page', 1),
        'page_size': request.GET.get('page_size', ''),
        'search': request.GET.get('search', ''),
        'state': request.GET.get('state', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'line': request.GET.get('line', '')
    }
    query_string = '&'.join([f'{key}={value}' for key, value in params.items() if value])

    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Le rapport n\'existe pas'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    if report.state == 'Confirmé':
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state

    refusal_reason = '/'

    if old_state != 'Brouillon':
        refusal_reason = 'Corrigée.'
    
    report.state = 'Confirmé'
    
    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason=refusal_reason, report=report)
    report.save()
    validation.save()
    report.save()

    if report.site.address:
        recipient_list = report.site.address.split('&')
    else:
        recipient_list = ['benshamou@gmail.com'] 
     
    #recipient_list = ['benshamou@gmail.com']

    messages.success(request, 'Rapport validé avec succès')
    subject, formatHtml = getMail('confirm', report, request.user.fullname, old_state == 'Brouillon')
    send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)


    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
    return redirect(redirect_url)

@login_required(login_url='login')
def cancelReport(request, pk):

    params = {
        'page': request.GET.get('page', 1),
        'page_size': request.GET.get('page_size', ''),
        'search': request.GET.get('search', ''),
        'state': request.GET.get('state', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'line': request.GET.get('line', '')
    }
    query_string = '&'.join([f'{key}={value}' for key, value in params.items() if value])
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Le rapport n\'existe pas'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    report.state = 'Annulé'
    
    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason='/', report=report)
    report.save()
    validation.save()

    # if old_state != 'Brouillon':    
    #     if report.site.address:
    #         recipient_list = report.site.address.split('&')
    #     else:
    #         recipient_list = ['benshamou@gmail.com']
    #     #recipient_list = ['benshamou@gmail.com']
    #     subject, formatHtml = getMail('cancel', report, request.user.fullname)
    #     send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)
        
    messages.success(request, 'Report Annulé successfully' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
    return redirect(redirect_url)

@login_required(login_url='login')
@DI_GS_required
def validateReport(request, pk, actor):
    
    params = {
        'page': request.GET.get('page', 1),
        'page_size': request.GET.get('page_size', ''),
        'search': request.GET.get('search', ''),
        'state': request.GET.get('state', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'line': request.GET.get('line', '')
    }
    query_string = '&'.join([f'{key}={value}' for key, value in params.items() if value])

    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(request, 'Le rapport n\'existe pas')
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    if (report.state == 'Validé par GS' and actor == 'GS') or (report.state == 'Validé par DI' and actor == 'DI'):
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state
    if report.state == 'Confirmé' and actor == 'GS':
        report.state = 'Validé par GS'
    elif report.state == 'Validé par GS' and actor == 'DI':
        report.state = 'Validé par DI'

    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason='/', report=report)
    report.save()
    validation.save()

    # if report.site.address:
    #     recipient_list = report.site.address.split('&')
    # else:
    #     recipient_list = ['benshamou@gmail.com']
    # #recipient_list = ['benshamou@gmail.com']

    # subject, formatHtml = getMail('validate', report, request.user.fullname)
    # send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)

    messages.success(request, 'Rapport validé avec succès' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
    return redirect(redirect_url)

@login_required(login_url='login')
@DI_GS_required
def refuseReport(request, pk, actor):
    
    params = {
        'page': request.GET.get('page', 1),
        'page_size': request.GET.get('page_size', ''),
        'search': request.GET.get('search', ''),
        'state': request.GET.get('state', ''),
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', ''),
        'line': request.GET.get('line', '')
    }
    query_string = '&'.join([f'{key}={value}' for key, value in params.items() if value])

    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Le rapport n\'existe pas'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    if (report.state == 'Refusé par GS' and actor == 'GS') or (report.state == 'Refusé par DI' and actor == 'DI'):
        messages.success(request, 'Rapport refusé avec succès' )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    if report.state == 'Confirmé' and actor == 'GS':
        report.state = 'Refusé par GS'
    elif report.state == 'Validé par GS' and actor == 'DI':
        report.state = 'Refusé par DI'
    
    new_state = report.state
    actor = request.user
    refusal_reason = request.POST.get('refusal_reason')

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason=refusal_reason, report=report)
    report.save()
    validation.save()

    if report.site.address:
        recipient_list = report.site.address.split('&')
    else:
        recipient_list = ['benshamou@gmail.com']
     
    #recipient_list = ['benshamou@gmail.com']

    subject, formatHtml = getMail('refuse', report, request.user.fullname, refusal_reason=refusal_reason)
    send_mail(subject, "", 'Puma Production', recipient_list, html_message=formatHtml)

    messages.success(request, 'Rapport refusé avec succès' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
    return redirect(redirect_url)
    
def getMail(action, report, fullname, old_state = False, refusal_reason = '/'):

    subject = 'Rapport de production ' + '[' + str(report.id) + ']' + ' - '  + report.team.__str__()
    address = 'http://myreporting.grupopuma-dz.com/report/'
    message = ''''''
    if action == 'confirm':
            if old_state:
                taux_nbr = 0
                if report.line.obj_ctd > 0 and report.used_time > 0:
                    relative_time_spent = report.used_time / report.shift.passed_time
                    real_obj = report.line.obj_ctd * relative_time_spent
                    taux_nbr = report.qte_tn / real_obj
                    taux_nbr = taux_nbr * 100
                    taux_nbr = round(taux_nbr, 2)
                taux = str(taux_nbr) + '%'
                message = '''
                <p>Bonjour l'équipe,</p>
                <p>Un rapport a été créé par <b style="color: #002060">''' + report.creator.fullname + '''</b> <b>(''' + report.line.designation + ''')</b>''' + ''' le <b>''' + str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '''</b>:</p>
                <ul>
                    <li><b>N° Lot :</b> <b style="color: #002060">''' + report.line.prefix_line + '''''' + str(report.n_lot).zfill(3) + '''/''' + report.prod_day.strftime("%y") + '''</b></li>
                    <li><b>Produit :</b> <b style="color: #002060">''' + report.prod_product.designation + '''</b></li>
                    <li><b>Date de production :</b> <b style="color: #002060">''' + str(report.prod_day) + '''</b></li>
                    <li><b>Équipe :</b> <b style="color: #002060">''' + report.team.designation + '''</b></li>
                    <li><b>Horaire :</b> <b style="color: #002060">''' + report.shift.__str__() + '''</b></li>
                    <li><b>Temps Utilisé :</b> <b style="color: #002060">''' + str(report.used_time) + '''h</b></li>
                    <li><b>Nombre Mélange :</b> <b style="color: #002060">''' + str(report.nbt_melange) + '''</b></li>
                    <li><b>Nombre ''' + report.prod_product.unite.conditionnement + '''   Produit :</b> <b style="color: #002060">''' + str(report.qte_sac_prod) + '''</b></li>
                    <li><b>Quantité :</b> <b style="color: #002060">''' + str(report.qte_tn) + ''' ''' + report.prod_product.unite.designation + '''</b></li>
                    <li><b>Objectif par shift :</b> <b style="color: #002060">''' + taux + '''</b></li>
                    <li><b>Nombre de sacs rébutés :</b> <b style="color: #002060">''' + str(report.qte_sac_reb) + '''</b></li>
                    <li><b>Nombre de sacs recyclés :</b> <b style="color: #002060">''' + str(report.qte_sac_rec) + '''</b></li>'''
                if report.site.designation == 'Constantine':
                    message += '''    <li><b>Citerne GPL 1 :</b> <b style="color: #002060">''' + str(report.gpl_1) + '''%</b></li>
                    <li><b>Citerne GPL 2 :</b> <b style="color: #002060">''' + str(report.gpl_2) + '''%</b></li>'''
                message += '''</ul>'''

                if report.arrets():
                    message += '''</br><p><b>Avec un total d'heures d'arrêt : </b><b style="color: #002060">''' + str(report.total_arrets) + '''</b></p>'''
                    arrets = report.arrets() 
                    message += '''</br></br><h4> L'équipe de production a eu ''' + str(len(arrets)) + ''' arrêts:</h4>
                    <ul>'''
                    for arret in arrets:
                        message += '''<li><b style="color: #002060">''' + arret.__str__() + '''</b></li>'''
                    message += '''</ul>'''
                
                message += '''</br><h4>Produits consommés: </h4>
                <ul>'''
                for mpconsumed in report.mpconsumeds() :
                    message += '''<li><b style="color: #002060">''' + mpconsumed.__str__() + '''</b></li>'''
                message += '''</ul>'''
                
                message += '''</br><h4>États de silos: </h4>
                <ul>'''
                for etatsilo in report.etatsilos() :
                    message += '''<li><b style="color: #002060">''' + etatsilo.__str__() + '''</b></li>'''
                message += '''</ul>'''
                
                message += '''<p>Pour plus de détails, veuillez visiter <a href="''' + address + str(report.id) +'''/">''' + address + str(report.id) +'''/</a>.</p>'''
            else:
                message += '''<p><b style="color: #002060">''' + fullname + '''</b><b>(''' + report.line.designation + ''')</b> a mis à jour son rapport, vous pouvez le vérifier ici: ''' + address + str(report.id) + '''/</p>'''

    elif action == 'cancel':
        message = '''<p><b>Le rapport [''' + str(report.id) + ''']</b> a été  <b>annulé</b> par <b>''' + fullname + '''</b><b>(''' + report.line.designation + ''')</b></p>
        </br>

        <p>Pour plus de détails, veuillez visiter <a href="''' + address + str(report.id) +'''/">''' + address + str(report.id) +'''/</a>.</p>'''

    elif action == 'refuse':
        message = '''<p><b>Le rapport [''' + str(report.id) + ''']</b> a été  <b>refusé</b> par <b>''' + fullname + '''</b><b>(''' + report.line.designation + ''')</b></p>
        </br>
        <p><b>Motif: ''' + refusal_reason + '''</b></p></br>

        <p>Pour plus de détails, veuillez visiter <a href="''' + address + str(report.id) +'''/">''' + address + str(report.id) +'''/</a>.</p>'''

    elif action == 'validate':
        message = '''<p><b>Le rapport [''' + str(report.id) + ''']</b> a été <b>validé</b> par <b>''' + fullname + '''</b><b>(''' + report.line.designation + ''')</b>
    
    <p>Pour plus de détails, veuillez visiter <a href="''' + address + str(report.id) +'''/">''' + address + str(report.id) +'''/</a>.</p>'''

    return subject, format_html(message)
    

#PLANNINGS

@login_required(login_url='login')
@admin_or_di_required
def planning_initial_view(request):
    if request.method == 'POST':
        form = PlanningInitialForm(request.POST)
        if form.is_valid():
            request.session['line_id'] = form.cleaned_data['line'].id
            request.session['shift_ids'] = [shift.id for shift in form.cleaned_data['shifts']]
            return redirect('planning_details')
    else:
        form = PlanningInitialForm(user=request.user)
    
    return render(request, 'planning_initial.html', {'form': form})

@login_required(login_url='login')
@admin_or_di_required
def planning_details_view(request):
    line_id = request.session.get('line_id')
    shift_ids = request.session.get('shift_ids', [])
    
    if not line_id or not shift_ids:
        return redirect('planning_initial')
    
    line = get_object_or_404(Line, id=line_id)
    shifts = Horaire.objects.filter(id__in=shift_ids)
    products = Product.objects.all()  
    class PlanLineForm(forms.Form):
        date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control bg-light'}))
        products = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=forms.SelectMultiple(attrs={'class': 'form-select select2'}))
        DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput())
    
    if request.method == 'POST':
        shift_forms = []
        forms_valid = True
        
        for shift in shifts:
            prefix = f'shift_{shift.id}_line'
            PlanLineFormSet = formset_factory(PlanLineForm, extra=0, can_delete=True)
            formset = PlanLineFormSet(request.POST, prefix=prefix)
            
            if formset.is_valid():
                shift_forms.append({'shift': shift, 'formset': formset})
            else:
                forms_valid = False
                break
        
        if forms_valid:
            planning = Planning.objects.create(creator=request.user, line=line)
            for shift_form in shift_forms:
                shift = shift_form['shift']
                formset = shift_form['formset']
                plan = Plan.objects.create(planning=planning, shift=shift)
                for form_data in formset.cleaned_data:
                    if not form_data.get('DELETE', False):
                        plan_line = PlanLine.objects.create(plan=plan, date=form_data['date'])
                        plan_line.products.set(form_data['products'])
            
            return redirect('view_planning', pk=planning.id)
    
    shifts_data = []
    for shift in shifts:
        PlanLineFormSet = formset_factory(PlanLineForm, extra=1, can_delete=True)
        formset = PlanLineFormSet(prefix=f'shift_{shift.id}_line')
        shifts_data.append({'shift': shift, 'lines': [{'form': form} for form in formset], 'management_form': formset.management_form })
    
    context = {'line': line, 'shifts': shifts_data, 'products': products}
    return render(request, 'planning_details.html', context)

@login_required(login_url='login')
@admin_or_di_required
def plannings_list_view(request):

    plannings = Planning.objects.all()
    filteredData = PlanningFilter(request.GET, queryset=plannings)
    plannings = filteredData.qs
    
    page_size = request.GET.get('page_size', 12)
    paginator = Paginator(plannings, page_size)
    page_number = request.GET.get('page', 1)
    page = paginator.get_page(page_number)
    
    context = {'page': page, 'filteredData': filteredData }
    
    return render(request, 'plannings_list.html', context)

@login_required(login_url='login')
@admin_or_di_required
def view_planning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.error(request, 'Le planning n\'existe pas')
        return redirect('plannings')
    
    plans = Plan.objects.filter(planning=planning)
    
    plan_data = []
    for plan in plans:
        plan_lines = PlanLine.objects.filter(plan=plan)
        plan_detail = {'shift': plan.shift, 'lines': []}
        
        for line in plan_lines:
            products = line.products.all()
            line_detail = {'date': line.date, 'products': products}
            plan_detail['lines'].append(line_detail)
        
        plan_data.append(plan_detail)
    
    context = {'planning': planning,'plan_data': plan_data}
    
    query_params = {}
    if 'page' in request.GET:
        query_params['page'] = request.GET['page']
    if 'page_size' in request.GET:
        query_params['page_size'] = request.GET['page_size']
    if 'search' in request.GET:
        query_params['search'] = request.GET['search']
    
    context['query_params'] = query_params
    
    return render(request, 'view_planning.html', context)

@login_required(login_url='login')
@admin_or_di_required
def delete_planning(request, pk):
    try:
        planning = Planning.objects.get(id=pk)
    except Planning.DoesNotExist:
        messages.error(request, 'Le planning n\'existe pas')
        url_path = reverse('plannings')
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    planning.delete()
    messages.success(request, 'Planning supprimé avec succès')
    
    url_path = reverse('plannings')
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

@login_required
@admin_or_di_required
def notify_planning(request):
    planning_id = request.POST.get('planning_id')

    if not planning_id:
        return JsonResponse({'success': False, 'message': 'Identifiant de planning manquant.'})
    
    try:
        planning = get_object_or_404(Planning, id=planning_id)

        if planning.line.site.address:
            addresses = planning.line.site.address.split('&')
        else:
            addresses = ['mohammed.benslimane@groupe-hasnaoui.com']

        plan_lines = planning.plans.prefetch_related('plan_lines__products')
        data = {}
        shift_names = sorted(set(plan.shift.name for plan in plan_lines))

        all_dates = [plan_line.date for plan in plan_lines for plan_line in plan.plan_lines.all()]

        min_date = min(all_dates).strftime("%d/%m/%Y") if all_dates else None
        max_date = max(all_dates).strftime("%d/%m/%Y") if all_dates else None

        for plan in plan_lines:
            for plan_line in plan.plan_lines.all():
                date_str = plan_line.date.strftime("%d/%m/%Y")
                day_name = plan_line.date.strftime("%A").upper()
                products = ", ".join([p.designation for p in plan_line.products.all()])

                if date_str not in data:
                    data[date_str] = {"day": day_name, "shifts": {s: "" for s in shift_names}}
                
                data[date_str]["shifts"][plan.shift.name] = products or ""

        context = {"planning": planning, "data": data, "shift_names": shift_names, "min_date": min_date, "max_date": max_date}
        subject = f'Planning de Production - {planning.line}'
        html_message = render_to_string('email_template.html', context)
        email = EmailMultiAlternatives(subject, None, 'Puma Trans', addresses)
        email.attach_alternative(html_message, "text/html") 
        email.send()    

        return JsonResponse({'success': True, 'message': f'Le planning a été notifié avec succès à {len(addresses)} destinataire(s).'})
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error sending planning notification: {str(e)}")
        return JsonResponse({'success': False, 'message': f'Une erreur est survenue lors de l\'envoi: {str(e)}'})


