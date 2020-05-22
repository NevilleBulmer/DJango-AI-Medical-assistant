# Class which handles all entry point url patterns.
from django.conf.urls import patterns, include, url
from django.contrib import admin

# Set admin to auto discover.
admin.autodiscover()

# Url patterns, I.e. all url's for the application.
urlpatterns = patterns('',
    # Pattern for the admin directory.
    url(r'^admin/', include(admin.site.urls)),
    # Pattern for the root directory, I.e. this will load the actual applications url's.
    url(r'^', include('health.urls', namespace='health'))
)
