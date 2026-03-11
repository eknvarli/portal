from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('requests/new/', views.create_service_request, name='create_service_request'),
    path('finance/', views.finance_overview, name='finance_overview'),
    path('files/', views.file_center, name='file_center'),
    path('approve-proposal/<int:proposal_id>/', views.approve_proposal, name='approve_proposal'),
]
