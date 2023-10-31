from django.shortcuts import render
from .models import User, Site, Line, Team
from django.shortcuts import render, redirect
import requests
import json
from .forms import *
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
import uuid
from .filters import *
from django.urls import reverse
from django.core.paginator import Paginator


# DECORATORS

def login_success(request):
    user = request.user
    if user.is_authenticated:
        if user.role != 'Admin':
            return redirect("list_report")
    return redirect("home")

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'Admin' or request.user.is_admin:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, '403.html', status=403)
    return wrapper

def admin_only_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'Admin':
            return view_func(request, *args, **kwargs)
        else:
            return render(request, '403.html', status=403)
    return wrapper

def DI_GS_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['Admin', 'Gestionnaire de stock', 'Directeur Industriel']:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, '403.html', status=403)
    return wrapper



def page_not_found(request, exception):
    return render(request, '404.html', status=404)


@login_required(login_url='login')
@admin_only_required
def homeView(request):

    context = {
        'content': 'content', 
    }
    return render(request, 'home.html', context)


# USERS

@login_required(login_url='login')
@admin_only_required
def refreshUsersList(request):
    
    usernames = User.objects.values_list('username', flat=True)
    
    API_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'
    GROUP_Users = 'https://api.ldap.groupe-hasnaoui.com/get/users/group/PUMA-PRD?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJUb2tlbiI6IkZvciBEU0kiLCJVc2VybmFtZSI6ImFjaG91cl9hciJ9.aMy1LUzKa6StDvQUX54pIvmjRwu85Fd88o-ldQhyWnE'

    response = requests.get(API_Users)
    response_ = requests.get(GROUP_Users)

    if response.status_code == 200 and response_.status_code == 200:
        data = json.loads(response.content)
        group_users = json.loads(response_.content)['members']

        new_users_list = [user for user in data['users'] if user['fullname'] in group_users and user['AD2000'] not in usernames]

        for user in new_users_list:
            user = User(username= user['AD2000'], password='password', fullname=user['fullname'], role='Nouveau', is_admin=False, first_name= user['fname'], email= user['mail'], last_name = user['lname'])
            user.save()
    else:
        print('Error: could not fetch data from API')

    cache_param = str(uuid.uuid4())
    url_path = reverse('new_users')
    redirect_url = f'{url_path}?cache={cache_param}'

    return redirect(redirect_url)

@login_required(login_url='login')
@admin_only_required
def editUserView(request, id):
    user = User.objects.get(id=id)
    selectedLines = [line.id for line in user.lines.all()]
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('users')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)

    context = {'form': form, 'user_to_edit': user, 'selectedLines': selectedLines}

    return render(request, 'edit_user.html', context)

@login_required(login_url='login')
@admin_only_required
def deleteUserView(request, id):
    user = User.objects.get(id=id)
    user.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse(request.GET.get('redirect_url', 'users').strip('/'))

    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_only_required
def listUsersView(request):

    users = User.objects.exclude(role='Nouveau').exclude(username='admin').order_by('id')
    filteredData = UserFilter(request.GET, queryset=users)
    users = filteredData.qs
    selectedLines = request.GET.getlist('line')

    if len(selectedLines) > 0:
        users = users.filter(lines__in=selectedLines)

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page, 'filtredData': filteredData, 'selectedLines': selectedLines,
    }
    return render(request, 'users_list.html', context)

@login_required(login_url='login')
@admin_only_required
def listNewUsersView(request):

    users = User.objects.filter(role='Nouveau').order_by('id')
    filteredData = UserFilter(request.GET, queryset=users)
    users = filteredData.qs

    paginator = Paginator(users, 10) 
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'page': page, 'filtredData': filteredData,
    }

    return render(request, 'users_list.html', context)

@login_required(login_url='login')
@admin_only_required
def userDetailsView(request, id):
  user = User.objects.get(id=id)
  context = {
    'user_details': user,
  }
  return render(request, 'user_details.html', context)


# AUTHENTIFICATION

class CustomLoginView(LoginView):
    template_name = 'login.html'
    form_class = CustomLoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse_lazy('home'))
        return super().dispatch(request, *args, **kwargs)

def logoutView(request):
    logout(request)
    return redirect('login')

# LOCATION AND TEAMS

@login_required(login_url='login')
@admin_required
def listLocationTeams(request):
    location_teams = Site.objects.all().order_by('id')
    filteredData = SiteFilter(request.GET, queryset=location_teams)
    location_teams = filteredData.qs
    paginator = Paginator(location_teams, 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'filtredData': filteredData,
    }
    return render(request, 'list_location_teams.html', context)

# SITES

@login_required(login_url='login')
@admin_required
def deleteSiteView(request, id):
    site = Site.objects.get(id=id)
    site.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('location_teams')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createSiteView(request):
    form = SiteForm()
    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('location_teams')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form, 'selectedHoraire': []}

    return render(request, 'site_form.html', context)

@login_required(login_url='login')
@admin_required
def editSiteView(request, id):
    site = Site.objects.get(id=id)
    form = SiteForm(instance=site)

    selectedHoraire = [horaire.id for horaire in site.horaires.all()]

    if request.method == 'POST':
        form = SiteForm(request.POST, request.FILES, instance=site)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('location_teams')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form, 'site': site, 'selectedHoraire': selectedHoraire}

    return render(request, 'site_form.html', context)


# LINES


@login_required(login_url='login')
@admin_required
def deleteLineView(request, id):
    line = Line.objects.get(id=id)
    line.delete()
    redirect_url = request.GET.get('redirect_url', 'location_teams')
    page = request.GET.get('page', '1')
    cache_param = str(uuid.uuid4())
    if redirect_url == 'location_teams':
        url_path = reverse('location_teams')
        redirect_url = f'{url_path}?cache={cache_param}&page={page}'
        return redirect(redirect_url)
    if 'site_' in redirect_url:
        id_site = redirect_url.split('_')[1]
        url_path = reverse('edit_site', args=[id_site])
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    url_path = reverse('location_teams')
    redirect_url = f'{url_path}?cache={cache_param}&page={page}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createLineView(request):
    site = request.GET.get('site', None)
    form = LineForm(site=site)
    
    if request.method == 'POST':
        form = LineForm(request.POST)
        if form.is_valid():
            cache_param = str(uuid.uuid4())
            form.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if 'site_' in redirect_url:
                id_site = redirect_url.split('_')[1]
                url_path = reverse('edit_site', args=[id_site])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form}

    return render(request, 'line_form.html', context)

@login_required(login_url='login')
@admin_required
def editLineView(request, id):
    line = Line.objects.get(id=id)
    form = LineForm(instance=line)
    if request.method == 'POST':
        form = LineForm(request.POST, instance=line)
        cache_param = str(uuid.uuid4())
        if form.is_valid():
            form.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if redirect_url == 'location_teams':
                url_path = reverse('location_teams')
                redirect_url = f'{url_path}?cache={cache_param}&page={page}'
                return redirect(redirect_url)
            if 'site_' in redirect_url:
                id_site = redirect_url.split('_')[1]
                url_path = reverse('edit_site', args=[id_site])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form, 'line': line}
    return render(request, 'line_form.html', context)


# TEAMS

@login_required(login_url='login')
@admin_required
def deleteTeamView(request, id):
    team = Team.objects.get(id=id)
    team.delete()
    redirect_url = request.GET.get('redirect_url', 'location_teams')
    page = request.GET.get('page', '1')
    cache_param = str(uuid.uuid4())
    if redirect_url == 'location_teams':
        cache_param = str(uuid.uuid4())
        url_path = reverse('location_teams')
        redirect_url = f'{url_path}?cache={cache_param}&page={page}'
        return redirect(redirect_url)
    if 'line_' in redirect_url:
        id_line = redirect_url.split('_')[1]
        url_path = reverse('edit_line', args=[id_line])
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    url_path = reverse('location_teams')
    redirect_url = f'{url_path}?cache={cache_param}&page={page}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createTeamView(request):

    line = request.GET.get('line', None)

    form = TeamForm(user = request.user, line = line)

    if request.method == 'POST':
        form = TeamForm(request.POST, user = request.user, line = line)
        if form.is_valid():
            cache_param = str(uuid.uuid4())
            designation = form.cleaned_data['designation']
            line = form.cleaned_data['line']
            team = Team(designation=designation, line=line)
            team.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if redirect_url == 'location_teams':
                url_path = reverse('location_teams')
                redirect_url = f'{url_path}?cache={cache_param}&page={page}'
                return redirect(redirect_url)
            if 'line_' in redirect_url:
                id_line = redirect_url.split('_')[1]
                url_path = reverse('edit_line', args=[id_line])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form}

    return render(request, 'team_form.html', context)

@login_required(login_url='login')
@admin_required
def editTeamView(request, id):
    team = Team.objects.get(id=id)
    form = TeamForm(instance=team, user = request.user)

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        cache_param = str(uuid.uuid4())
        if form.is_valid():
            form.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if redirect_url == 'location_teams':
                url_path = reverse('location_teams')
                redirect_url = f'{url_path}?cache={cache_param}&page={page}'
                return redirect(redirect_url)
            if 'line_' in redirect_url:
                id_line = redirect_url.split('_')[1]
                url_path = reverse('edit_line', args=[id_line])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'team': team}

    return render(request, 'team_form.html', context)

# Silos

@login_required(login_url='login')
@admin_required
def deleteSiloView(request, id):
    silo = Silo.objects.get(id=id)
    silo.delete()
    redirect_url = request.GET.get('redirect_url', 'location_teams')
    page = request.GET.get('page', '1')
    cache_param = str(uuid.uuid4())
    if redirect_url == 'location_teams':
        cache_param = str(uuid.uuid4())
        url_path = reverse('location_teams')
        redirect_url = f'{url_path}?cache={cache_param}&page={page}'
        return redirect(redirect_url)
    if 'line_' in redirect_url:
        id_line = redirect_url.split('_')[1]
        url_path = reverse('edit_line', args=[id_line])
        redirect_url = f'{url_path}?cache={cache_param}'
        return redirect(redirect_url)
    url_path = reverse('location_teams')
    redirect_url = f'{url_path}?cache={cache_param}&page={page}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createSiloView(request):

    line = request.GET.get('line', None)

    form = SiloForm(user = request.user, line = line)

    if request.method == 'POST':
        form = SiloForm(request.POST, user = request.user, line = line)
        if form.is_valid():
            cache_param = str(uuid.uuid4())
            designation = form.cleaned_data['designation']
            line = form.cleaned_data['line']
            silo = Silo(designation=designation, line=line)
            silo.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if redirect_url == 'location_teams':
                url_path = reverse('location_teams')
                redirect_url = f'{url_path}?cache={cache_param}&page={page}'
                return redirect(redirect_url)
            if 'line_' in redirect_url:
                id_line = redirect_url.split('_')[1]
                url_path = reverse('edit_line', args=[id_line])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)

    context = {'form': form}

    return render(request, 'silo_form.html', context)

@login_required(login_url='login')
@admin_required
def editSiloView(request, id):
    silo = Silo.objects.get(id=id)
    form = SiloForm(instance=silo, user = request.user)

    if request.method == 'POST':
        form = SiloForm(request.POST, instance=silo)
        cache_param = str(uuid.uuid4())
        if form.is_valid():
            form.save()
            redirect_url = request.GET.get('redirect_url', 'location_teams')
            page = request.GET.get('page', '1')
            if redirect_url == 'location_teams':
                url_path = reverse('location_teams')
                redirect_url = f'{url_path}?cache={cache_param}&page={page}'
                return redirect(redirect_url)
            if 'line_' in redirect_url:
                id_line = redirect_url.split('_')[1]
                url_path = reverse('edit_line', args=[id_line])
                redirect_url = f'{url_path}?cache={cache_param}'
                return redirect(redirect_url)
            url_path = reverse('location_teams')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'silo': silo}

    return render(request, 'silo_form.html', context)


# HORAIRE

@login_required(login_url='login')
@admin_required
def listHoraireView(request):
    horaires = Horaire.objects.all().order_by('id')
    paginator = Paginator(horaires, 8)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page, 'horaires': horaires, 
    }
    return render(request, 'list_horaire.html', context)

@login_required(login_url='login')
@admin_required
def deleteHoraireView(request, id):
    horaire = Horaire.objects.get(id=id)
    horaire.delete()
    cache_param = str(uuid.uuid4())
    url_path = reverse('horaires')
    redirect_url = f'{url_path}?cache={cache_param}'
    return redirect(redirect_url)

@login_required(login_url='login')
@admin_required
def createHoraireView(request):
    form = HoraireForm()
    if request.method == 'POST':
        form = HoraireForm(request.POST)
        if form.is_valid():
            hour_start = form.cleaned_data['hour_start']
            minutes_start = form.cleaned_data['minutes_start']
            hour_end = form.cleaned_data['hour_end']
            minutes_end = form.cleaned_data['minutes_end']
            horaire = Horaire(hour_start = hour_start, minutes_start = minutes_start, hour_end = hour_end, minutes_end = minutes_end)
            horaire.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('horaires')
            redirect_url = f'{url_path}?cache={cache_param}'
            return redirect(redirect_url)
    context = {'form': form}
    return render(request, 'horaire_form.html', context)

@login_required(login_url='login')
@admin_required
def editHoraireView(request, id):
    horaire = Horaire.objects.get(id=id)
    form = HoraireForm(instance=horaire)
    if request.method == 'POST':
        form = HoraireForm(request.POST, instance=horaire)
        if form.is_valid():
            form.save()
            cache_param = str(uuid.uuid4())
            url_path = reverse('horaires')
            page = request.GET.get('page', '1')
            redirect_url = f'{url_path}?cache={cache_param}&page={page}'
            return redirect(redirect_url)
    context = {'form': form, 'horaire': horaire}

    return render(request, 'horaire_form.html', context)
