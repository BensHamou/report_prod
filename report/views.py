from django.shortcuts import render
from account.models import *
from .models import *
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from account.views import admin_required, RP_GS_required
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
from django.conf import settings


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
        if not (arret.report.state in ['Brouillon','Refusé par GS', 'Refusé par RP'] and (request.user.role == "Gestionnaire de production" and request.user == arret.report.creator or request.user.role == 'Admin')):
            return render(request, '403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key,0)


# PRODUCTS
@login_required(login_url='login')
@admin_required
def listProductList(request):
    products = Product.objects.filter(line__in=request.user.lines.all()).order_by('id')
    filteredData = ProductFilter(request.GET, queryset=products, user = request.user)
    products = filteredData.qs
    paginator = Paginator(products, 8)
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
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
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
    paginator = Paginator(products, 8)
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
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
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
    paginator = Paginator(types, 8)
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
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
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
    paginator = Paginator(reasons, 10)
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
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'

            return redirect(redirect_url)

    context = {'form': form, 'reason': reason}

    return render(request, 'reason_form.html', context)

#REPORTS

class ReportInline():
    form_class = ReportForm
    model = Report
    template_name = "report_form.html"    
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['lines'] = self.request.user.lines.all()
        kwargs['team'] = self.request.user.team
        kwargs['site'] = self.request.user.lines.all().first().site
        kwargs['teams'] = Team.objects.filter(line__in=self.request.user.lines.all())
        kwargs['products'] = Product.objects.filter(line__in=self.request.user.lines.all())
        return kwargs

    def form_valid(self, form):
        named_formsets = self.get_named_formsets()
        if not all((x.is_valid() for x in named_formsets.values())):
            return self.render_to_response(self.get_context_data(form=form))
        
        report = form.save(commit=False)
        report.creator = self.request.user 
        if not report.state or report.state == 'Brouillon':
            report.state = 'Brouillon'
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


class ReportCreate(ReportInline, CreateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportCreate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        if self.request.method == "GET":
            return {
                'arrets': ArretsFormSet(prefix='arrets', form_kwargs={'user': self.request.user}),
                'consumed_products': MPConsumedsFormSet(prefix='consumed_products'),
                'etatsilos': EtatSiloFormSet(prefix='etatsilos'),
            }
        else:
            return {
                'arrets': ArretsFormSet(self.request.POST or None, prefix='arrets', form_kwargs={'user': self.request.user}),
                'consumed_products': MPConsumedsFormSet(self.request.POST or None, prefix='consumed_products'),
                'etatsilos': EtatSiloFormSet(self.request.POST or None, prefix='etatsilos'),
            }

class ReportUpdate(ReportInline, UpdateView):

    def get_context_data(self, **kwargs):
        ctx = super(ReportUpdate, self).get_context_data(**kwargs)
        ctx['named_formsets'] = self.get_named_formsets()
        return ctx

    def get_named_formsets(self):
        return {
            'arrets': ArretsFormSet(self.request.POST or None, instance=self.object, prefix='arrets', form_kwargs={'user': self.request.user}),
            'consumed_products': MPConsumedsFormSet(self.request.POST or None, instance=self.object, prefix='consumed_products'),
            'etatsilos': EtatSiloFormSet(self.request.POST or None, instance=self.object, prefix='etatsilos'),
        }
    
class ReportDetail(DetailView):
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
    ordering = ['-date_modified']
        
    all_GP = ['Brouillon', 'Confirmé', 'Validé par GS', 'Validé par RP', 'Refusé par GS', 'Refusé par RP', 'Annulé']
    all_A = ['Confirmé', 'Validé par GS', 'Validé par RP', 'Refusé par GS', 'Refusé par RP', 'Annulé']
    all_GS = ['Confirmé', 'Validé par GS', 'Refusé par GS', 'Refusé par RP']
    all_RP = ['Validé par GS', 'Validé par RP', 'Refusé par RP']

    def get_filterset_kwargs(self, filterset_class):
        kwargs = super().get_filterset_kwargs(filterset_class)
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.user.role
        lines = self.request.user.lines.all()

        if role == 'Gestionnaire de production':
            queryset = queryset.filter(Q(creator=self.request.user) & Q(state__in=self.all_GP))

        elif role == 'Gestionnaire de stock':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_GS))
                
        elif role == 'Responsable de production':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_RP))

        elif role == 'Admin':
            queryset = queryset.filter(Q(line__in=lines) & Q(state__in=self.all_A))

        return queryset

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        paginator = Paginator(context['reports'], 8)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page'] = page_obj
        context['state_totals'] = self.get_state_totals()
        context['all_total'] = len(context['reports'])
        role_state = {'Gestionnaire de production': self.all_GP, 'Gestionnaire de stock': self.all_GS, 'Responsable de production': self.all_RP, 'Admin': self.all_A}
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
            request, 'Report Does not exit'
            )
        url_path = reverse('list_report')
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    report.delete()
    messages.success(
            request, 'Report deleted successfully'
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
            request, 'Arret Does not exit'
            )
        url_path = reverse('update_report', args=[arret.report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)

    arret.delete()
    messages.success(
            request, 'Arret deleted successfully'
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
    reason_stop_list = [{'id': reason_stop.id, 'designation': reason_stop.__str__()} for reason_stop in ReasonStop.objects.filter(type__in=type_stops)]

    return JsonResponse({'teams': team_list, 'products': product_list, 'type_stops': type_stop_list, 
                         'reason_stops': reason_stop_list, 'silos': silo_list, 'horaires_list': horaires_list})

@login_required(login_url='login')
def get_arretData_by_line(request):
    line_id = request.GET.get('line_id')
    if line_id == '':
        return JsonResponse({'type_stops': [], 'reason_stops': [] })
    type_stops = TypeStop.objects.filter(line_id=line_id)

    type_stop_list = [{'id': type_stop.id, 'designation': type_stop.__str__()} for type_stop in type_stops]
    reason_stop_list = [{'id': reason_stop.id, 'designation': reason_stop.__str__()} for reason_stop in ReasonStop.objects.filter(type__in=type_stops)]

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

    mp_list = [numo_product.id for numo_product in numo_products]

    return JsonResponse({'mp_list': mp_list })

@login_required(login_url='login')
@check_creator
def confirmReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Report Does not exit'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
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
    messages.success(request, 'Report Confirmé successfully')

    if old_state == 'Brouillon':
        subject = 'Rapport de production ' + '('+ report.site.designation +')'
        message = '''   Un rapport a été créé par ''' + request.user.fullname + '''(''' + report.line.designation + ''')''' + ''' :
        N° Lot : ''' + report.n_lot + ''' 
        Produit : ''' + report.prod_product.designation + '''
        Date de production : ''' + str(report.prod_day) + '''
        Équipe : ''' + report.team.designation + ''' - Horaire ''' + report.shift.__str__() + '''
        Qte : ''' + str(report.qte_tn) + ''' TN
        Avec un total d'heures d'arrêt : ''' + str(report.total_arrets)
            
        recipient_list = ['benshamou@gmail.com']

        send_mail(subject, message, 'Puma Production', recipient_list)

    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
def cancelReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Report Does not exit'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    report.state = 'Annulé'
    
    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason='/', report=report)
    report.save()
    validation.save()
        
    messages.success(request, 'Report Annulé successfully' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@RP_GS_required
def validateReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Report Does not exit'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    if request.user.role in ['Gestionnaire de stock', 'Admin'] and report.state == 'Confirmé':
        report.state = 'Validé par GS'
    elif request.user.role in ['Responsable de production', 'Admin'] and report.state == 'Validé par GS':
        report.state = 'Validé par RP'

    new_state = report.state
    actor = request.user

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason='/', report=report)
    report.save()
    validation.save()
        
    messages.success(request, 'Report validated successfully' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@RP_GS_required
def refuseReport(request, pk):
    try:
        report = Report.objects.get(id=pk)
    except Report.DoesNotExist:
        messages.success(
            request, 'Report Does not exit'
            )
        url_path = reverse('report_detail', args=[report.id])
        cache_param = str(uuid.uuid4())
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    
    old_state = report.state
    
    if request.user.role in ['Gestionnaire de stock', 'Admin'] and report.state == 'Confirmé':
        report.state = 'Refusé par GS'
    elif request.user.role in ['Responsable de production', 'Admin'] and report.state == 'Validé par GS':
        report.state = 'Refusé par RP'
    
    new_state = report.state
    actor = request.user
    refusal_reason = request.POST.get('refusal_reason')

    validation = Validation(old_state=old_state, new_state=new_state, actor=actor, refusal_reason=refusal_reason, report=report)
    report.save()
    validation.save()
        
    messages.success(request, 'Report refused successfully' )
    url_path = reverse('report_detail', args=[report.id])
    cache_param = str(uuid.uuid4())
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)