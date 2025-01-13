from django.urls import path
from . import views
from .views import SignUpView, CustomLoginView, verify_email, custom_logout
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.MainPageView.as_view(), name='main_page'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('verify/<int:user_id>/', verify_email, name='verify_email'),

    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/create/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('messages/<int:pk>/update/', views.MessageUpdateView.as_view(), name='message_update'),
    path('messages/<int:pk>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),

    path('', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/', views.MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', views.MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/create/', views.MailingCreateView.as_view(), name='mailing_create'),
    path('mailings/<int:pk>/update/', views.MailingUpdateView.as_view(), name='mailing_update'),
    path('mailings/<int:pk>/delete/', views.MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/status/', views.MailingStatusView.as_view(), name='mailing_status'),
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/block/', views.UserBlockView.as_view(), name='user_block'),
    path('mailing/<int:pk>/deactivate/', views.MailingDeactivateView.as_view(), name='mailing_deactivate'),

    path('statistics/', views.StatisticsView.as_view(), name='mailing_statistics'),
    path('logs/', views.MailingLogListView.as_view(), name='mailing_logs'),
    path('attempt-stats/', views.MailingAttemptStatsView.as_view(), name='mailing_attempt_stats'),
    path('attempt-stats/<int:pk>/', views.MailingAttemptDetailView.as_view(), name='mailing_attempt_detail'),
]