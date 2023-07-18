from django.urls import path, include
from . import views
from .views import CustomLoginView
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    path('login_success/', views.login_success, name='login_success'),

    path("dashboard/", views.homeView, name="home"),
    path("refresh-users/", views.refreshUsersList, name="refresh_users"),
    path("users/edit-user/<int:id>", views.editUserView, name="edit_user"),
    path("users/delete-user/<int:id>", views.deleteUserView, name="delete_user"),
    path("users/", views.listUsersView, name="users"),
    path("new_users/", views.listNewUsersView, name="new_users"),
    path('users/details/<int:id>', views.userDetailsView, name='details'),
    
    path('login/', CustomLoginView.as_view(), name='login'),
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.logoutView, name='logout'),

    path('location-teams/', views.listLocationTeams, name='location_teams'),

    # path('sites/', views.listSitesList, name='sites'),
    path("sites/delete-site/<int:id>", views.deleteSiteView, name="delete_site"),
    path("sites/edit-site/<int:id>", views.editSiteView, name="edit_site"),
    path("sites/create-site/", views.createSiteView, name="create_site"),

    path("lines/delete-line/<int:id>", views.deleteLineView, name="delete_line"),
    path("lines/edit-line/<int:id>", views.editLineView, name="edit_line"),
    path("lines/create-line/", views.createLineView, name="create_line"),

    # path('teams/', views.listTeamList, name='teams'),
    path("teams/delete-team/<int:id>", views.deleteTeamView, name="delete_team"),
    path("teams/edit-team/<int:id>", views.editTeamView, name="edit_team"),
    path("teams/create-team/", views.createTeamView, name="create_team"),

    # path('silos/', views.listSiloList, name='silos'),
    path("silos/delete-silo/<int:id>", views.deleteSiloView, name="delete_silo"),
    path("silos/edit-silo/<int:id>", views.editSiloView, name="edit_silo"),
    path("silos/create-silo/", views.createSiloView, name="create_silo"),

    path('horaires/', views.listHoraireView, name='horaires'),
    path("horaires/delete-horaire/<int:id>", views.deleteHoraireView, name="delete_horaire"),
    path("horaires/edit-horaire/<int:id>", views.editHoraireView, name="edit_horaire"),
    path("horaires/create-horaire/", views.createHoraireView, name="create_horaire"),
]

