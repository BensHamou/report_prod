from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('products/', views.listProductList, name='products'),
    path("products/delete-product/<int:id>", views.deleteProductView, name="delete_product"),
    path("products/edit-product/<int:id>", views.editProductView, name="edit_product"),
    path("products/create-product/", views.createProductView, name="create_product"),

    path("products/numo_products/", views.listNumoProductView, name="numo_products"),
    path("products/numo_products/delete-product/<int:id>", views.deleteNumoProductView, name="delete_numo_product"),
    path("products/numo_products/edit-product/<int:id>", views.editNumoProductView, name="edit_numo_product"),
    path("products/numo_products/create-product/", views.createNumoProductView, name="create_numo_product"),

    path('stopping-types/', views.listTypeStopList, name='types'),
    path("stopping-types/delete-type/<int:id>", views.deleteTypeStopView, name="delete_type"),
    path("stopping-types/edit-type/<int:id>", views.editTypeStopView, name="edit_type"),
    path("stopping-types/create-type/", views.createTypeStopView, name="create_type"),

    path('stopping-reasons/', views.listReasonStopList, name='reasons'),
    path("stopping-reasons/delete-reason/<int:id>", views.deleteReasonStopView, name="delete_reason"),
    path("stopping-reasons/edit-reason/<int:id>", views.editReasonStopView, name="edit_reason"),
    path("stopping-reasons/create-reason/", views.createReasonStopView, name="create_reason"),

    path('reports/', ReportList.as_view(), name='list_report'),
    path('', ReportList.as_view(), name='list_report'),
    path('report/create/', ReportCreate.as_view(), name='create_report'),
    path('report/<int:pk>/update/', ReportUpdate.as_view(), name='update_report'),
    path('report/<int:pk>/delete/', delete_report, name='delete_report'),
    path('report/<int:pk>/', ReportDetail.as_view(), name='report_detail'),
    path('delete-arret/<int:pk>/', delete_arret, name='delete_arret'),

    
    path('report/<int:pk>/confirm/', views.confirmReport, name='confirm_report'),
    path('report/<int:pk>/refuse/<str:actor>/', views.refuseReport, name='refuse_report'),
    path('report/<int:pk>/cancel/', views.cancelReport, name='cancel_report'),
    path('report/<int:pk>/validate/<str:actor>/', views.validateReport, name='validate_report'),

    path('report/get-data-by-line/', views.get_data_by_line, name='get_data_by_line'),
    path('report/get-arretData-by-line/', views.get_arretData_by_line, name='get_arretData_by_line'),
    path('report/get-reasons-by-type/', views.get_reasons_by_type, name='get_reasons_by_type'),
    path('report/get-numo-by-product/', views.get_numo_by_product, name='get_numo_by_product'),
    path('report/get-qte-by-product/', views.get_qte_per_container, name='get_qte_per_container'),
    path('report/get-max-by-shift/', views.get_shift_max, name='get_shift_max'),

    path('plannings/', views.plannings_list_view, name='plannings'),
    path('planning/line/', views.planning_initial_view, name='planning_initial'),
    path('planning/products/', views.planning_details_view, name='planning_details'),
    path('planning/<int:pk>/', views.view_planning, name='view_planning'),
    path('delete-planning/<int:pk>/', delete_planning, name='delete_planning'),
    path('notify-planning/', views.notify_planning, name='notify_planning'),

]

