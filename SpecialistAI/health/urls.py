# Class which handles all url patterns, I.e. a user clicks a link and navigates to a new page.
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from . import views

# Url patterns, I.e. all url's for the application.
urlpatterns = patterns('',
    # Pattern for the login page.
    url(r'login/?$', views.login_view, name='login'),
    # Pattern which will be used if the user wishes to logout.
    url(r'logout/?$', views.logout_view, name='logout'),
    # Pattern for displaying the users schedule.
    url(r'schedule/?$', views.schedule, name='schedule'),
    # Pattern for displaying the users current prescriptions.
    url(r'prescriptions/?$', views.prescriptions, name='prescriptions'),
    # Pattern for displaying the users current messages, I.e. send a new message.
    url(r'messages/?$', views.messages, name='messages'),
    # Pattern for displaying the users current conversations, I.e. past messages.
    url(r'messages/(\d+)/?$', views.conversation, name='conversation'),
    # Pattern for removing a prescription, requires specific account.
    url(r'delete_prescription/(\d+)/?$', views.delete_prescription, name='delete_prescription'),
    # Pattern for editing a prescription, requires specific account.
    url(r'edit_prescription/(\d+)?/?$', views.prescription_form, name='edit_prescription'),
    # Pattern for adding a prescription, requires specific account.
    url(r'add_prescription/?$', views.add_prescription_form, name='add_prescription'),
    # Pattern for removing a appointment, requires specific account.
    url(r'delete_appointment/(\d+)/?$', views.delete_appointment, name='delete_appointment'),
    # Pattern for editing an appointment, requires specific account.
    url(r'edit_appointment/(\d+)?/?$', views.appointment_form, name='edit_appointment'),
    # Pattern for adding an appointment, requires specific account.
    url(r'add_appointment/?$', views.add_appointment_form, name='add_appointment'),
    # Pattern for adding a group, I.e. messaging, requires specific account.
    url(r'add_group/?$', views.add_group, name='add_group'),
    # Pattern for displaying a user medical informaiton, I.e. a patients information, requires specific account.
    url(r'users/(\d+)/?$', views.medical_information, name='medical_information'),
    # Pattern for displaying a users information, I.e. a users profile.
    url(r'users/me/?$', views.my_medical_information, name='my_medical_information'),
    # Pattern for creating a new account.
    url(r'signup/?$', views.signup, name='signup'),
    # Pattern for exporting a users information, downloads a users information.
    url(r'users/(\d+)/info.json/?$', views.export, name='export'),
    # Pattern for exporting a users information, downloads a users information.
    url(r'users/me/info.json/?$', views.export_me, name='export_me'),
    # Pattern for detecting a user.
    url(r'users/?$', views.users, name='users'),
    # Pattern for displaying all logs for the application, I.e. has something changed,
    # and what, and who, requires specific account.
    url(r'logs/?$', views.logs, name='logs'),
    # Pattern for displaying the page media_gallery.html, I.e. a users documents.
    url(r'media_gallery/(\d+)/?$', views.media_gallery, name='media_gallery'),
    # Pattern for navigating to the home page.
    url(r'^/?$', views.home, name='home'),
)