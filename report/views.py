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
from datetime import timedelta, datetime
from django.db import transaction
from django.utils.dateparse import parse_date
from account.views import admin_or_di_required

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import locale

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
        if arret.report.state == 'Validé par GS' and request.user.role == 'Maintenancier':
            return view_func(request, *args, **kwargs)
        if request.user.role == 'Admin':
            return view_func(request, *args, **kwargs)
        if not (arret.report.state in ['Brouillon','Refusé par GS', 'Refusé par Maintenancier'] and 
                (request.user.role == "Gestionnaire de production" and request.user == arret.report.creator)):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

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
        if self.request.user.role == 'Maintenancier' and report.state == 'Validé par GS':
            return True
        if (report.creator != self.request.user or self.request.user.role != "Gestionnaire de production" or 
            report.state not in ['Brouillon','Refusé par GS','Refusé par Maintenancier']) and self.request.user.role != 'Admin':
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
        reports = Report.objects.filter(Q(creator=self.request.user), Q(line__in=lines) & Q(state='Refusé par GS') | Q(state='Refusé par Maintenancier'))
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
        kwargs['Maintenancier'] = self.request.user.role == 'Maintenancier'
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
        
    all_GP = ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par Maintenancier', 'Refusé par GS', 'Refusé par Maintenancier', 'Annulé']
    all_A = ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par Maintenancier', 'Refusé par GS', 'Refusé par Maintenancier', 'Annulé']
    all_GS = ['Confirmé', 'Validé par GS', 'Refusé par GS', 'Refusé par Maintenancier', 'Validé par Maintenancier']
    all_DI = ['Validé par GS', 'Validé par Maintenancier', 'Refusé par Maintenancier']
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
                
        elif role == 'Maintenancier':
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
        role_state = {'Gestionnaire de production': self.all_GP, 'Gestionnaire de stock': self.all_GS, 'Maintenancier': self.all_DI, 'Admin': self.all_A, 'Observateur': self.all_A, 'Nouveau': self.all_NV}
        context['role_state'] = role_state
        count_plannings = 0
        if self.request.user.do_notify and self.request.user.lines_to_notify.count() > 0:
            for planning in ProductionPlan.objects.filter(creator=self.request.user, to_date=datetime.today().date() + timedelta(days=1)):
                for line in planning.lines.all():
                    if ProductionPlan.objects.filter(lines__in=[line], from_date=planning.to_date + timedelta(days=1)).exists():
                        continue
                    if line in self.request.user.lines_to_notify.all():
                        count_plannings += 1
        context['count_plannings'] = count_plannings
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
        recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com'] 
     
    #recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']

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
    #         recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']
    #     #recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']
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
    
    if (report.state == 'Validé par GS' and actor == 'GS') or (report.state == 'Validé par Maintenancier' and actor == 'Maintenancier'):
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state
    if report.state == 'Confirmé' and actor == 'GS':
        report.state = 'Validé par GS'
    elif report.state == 'Validé par GS' and actor == 'Maintenancier':
        report.state = 'Validé par Maintenancier'

    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason='/', report=report)
    report.save()
    validation.save()

    # if report.site.address:
    #     recipient_list = report.site.address.split('&')
    # else:
    #     recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']
    # #recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']

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
    
    if (report.state == 'Refusé par GS' and actor == 'GS') or (report.state == 'Refusé par Maintenancier' and actor == 'Maintenancier'):
        messages.success(request, 'Rapport refusé avec succès' )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}&{query_string}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    if report.state == 'Confirmé' and actor == 'GS':
        report.state = 'Refusé par GS'
    elif report.state == 'Validé par GS' and actor == 'Maintenancier':
        report.state = 'Refusé par Maintenancier'
    
    new_state = report.state
    actor = request.user
    refusal_reason = request.POST.get('refusal_reason')

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason=refusal_reason, report=report)
    report.save()
    validation.save()

    if report.site.address:
        recipient_list = report.site.address.split('&')
    else:
        recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']
     
    #recipient_list = ['mohammed.benslimane@groupe-hasnaoui.com']

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
    
class CreateProductionPlanView(CreateView):
    model = ProductionPlan
    form_class = PlanSetupForm
    template_name = 'plan_setup.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.creator = self.request.user
        response = super().form_valid(form)
        
        plan = self.object
        lines = form.cleaned_data['lines']
        shifts = form.cleaned_data['shifts']
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        
        delta = to_date - from_date
        dates = [from_date + timedelta(days=i) for i in range(delta.days + 1)]
        
        with transaction.atomic():
            for line in lines:
                for date in dates:
                    for shift in shifts:
                        DailyAssignment.objects.create(plan=plan, line=line, date=date, shift=shift)
        return redirect('assign_products', plan_id=plan.id, line_id=lines.first().id)

    def get_success_url(self):
        plan = self.object
        first_line = plan.lines.first()
        return reverse('assign_products', kwargs={ 'plan_id': plan.id, 'line_id': first_line.id})

@login_required(login_url='login')
@admin_or_di_required
def assign_products(request, plan_id, line_id):
    plan = get_object_or_404(ProductionPlan, pk=plan_id)
    line = get_object_or_404(Line, pk=line_id)
    assignments = DailyAssignment.objects.filter(plan=plan, line=line).order_by('date', 'shift')

    all_lines = plan.lines.order_by('id')
    current_line_index = list(all_lines).index(line)
    is_last_line = current_line_index == len(all_lines) - 1

    form_dict = {}
    if request.method == 'POST':
        all_valid = True
        for assignment in assignments:
            form = DailyAssignmentForm(request.POST, prefix=f'assignment_{assignment.id}', instance=assignment, line=line)
            form_dict[assignment.id] = form
            if not form.is_valid():
                all_valid = False
        
        if all_valid:
            for form in form_dict.values():
                form.save()
            
            if not is_last_line:
                next_line = all_lines[current_line_index + 1]
                return redirect('assign_products', plan_id=plan.id, line_id=next_line.id)
            else:
                plan.is_completed = True
                plan.save()
                messages.success(request, "Production plan completed successfully!")
                return redirect('plan_detail', pk=plan.id)
    else:
        for assignment in assignments:
            form_dict[assignment.id] = DailyAssignmentForm(prefix=f'assignment_{assignment.id}', instance=assignment, line=line)

    dates = {}
    for assignment in assignments:
        if assignment.date not in dates:
            dates[assignment.date] = []
        dates[assignment.date].append(assignment)

    context = { 'plan': plan, 'line': line, 'dates': sorted(dates.items()), 'forms': form_dict, 'is_last_line': is_last_line }
    return render(request, 'assign_products.html', context)

@login_required(login_url='login')
@admin_or_di_required
def plan_detail(request, pk):
    plan = get_object_or_404(ProductionPlan, pk=pk)
    return render(request, 'plan_detail.html', {'plan': plan})

@login_required(login_url='login')
@admin_or_di_required
def list_production_plans(request):
    plans = ProductionPlan.objects.filter(lines__in=request.user.lines.all()).distinct().order_by('-date_created')
    filtered_plans = ProductionPlanFilter(request.GET, queryset=plans)
    plans = filtered_plans.qs
    page_size_param = request.GET.get('page_size')
    page_size = int(page_size_param) if page_size_param else 12
    paginator = Paginator(plans, page_size)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    context = {'page': page, 'filteredData': filtered_plans, 'page_size': page_size,}
    return render(request, 'plannings_list.html', context)

@login_required(login_url='login')
@admin_or_di_required
def delete_plan(request, pk):
    try:
        planning = ProductionPlan.objects.get(id=pk)
    except ProductionPlan.DoesNotExist:
        messages.error(request, 'Le planning n\'existe pas')
        url_path = reverse('plans')
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    planning.delete()
    messages.success(request, 'Planning supprimé avec succès')
    
    url_path = reverse('plans')
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@register.filter
def get_assignment(plan, arg_string):
    try:
        line_id, date_str, shift_id = arg_string.split(',')
        date = parse_date(date_str)
        print(plan, arg_string)
        return plan.assignments.filter(line_id=line_id,date=date,shift_id=shift_id).first()
    except (ValueError, AttributeError):
        return None
    

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")

@login_required
@admin_or_di_required
def notify_plan(request):
    plan_id = request.POST.get('planning_id')

    if not plan_id:
        return JsonResponse({'success': False, 'message': 'Identifiant de planning manquant.'})
    
    try:
        plan = get_object_or_404(ProductionPlan, id=plan_id)
        
        for line in plan.lines.all():
            if not line.site.address:
                continue
                
            dates_data = []
            for date in plan.date_range:
                shifts_data = []
                has_any_products = False
                
                for shift in plan.shifts.all():
                    assignment = plan.assignments.filter(line=line, date=date, shift=shift).first()
                    products = assignment.products.all() if assignment else []
                    if products:
                        has_any_products = True
                    shifts_data.append({'shift': shift, 'products': products, 'has_products': bool(products)})
                
                if has_any_products:
                    dates_data.append({'date': date, 'date_display': date.strftime("%d/%m/%Y"), 
                                       'day_name': date.strftime("%A").capitalize(), 'shifts': shifts_data})

            if not dates_data:
                continue

            context = {'plan': plan, 'line': line, 'dates': dates_data, 'shifts': plan.shifts.all(), 
                'from_date': plan.from_date.strftime("%d/%m/%Y"), 'to_date': plan.to_date.strftime("%d/%m/%Y")}
            
            html_message = render_to_string('planning/email_template.html', context)

            addresses = line.site.address.split('&')
            
            subject = f"Planning production - Ligne {line.designation} ({plan.from_date.strftime('%d/%m/%Y')} au {plan.to_date.strftime('%d/%m/%Y')})"
            email = EmailMultiAlternatives(subject=subject, body='', from_email='Puma Production', 
                                           to=addresses, reply_to=["noreply@grupopuma-dz.com"])
            email.attach_alternative(html_message, "text/html")
            email.send()
            
        return JsonResponse({'success': True, 'message': 'Notifications envoyées avec succès.'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'})



