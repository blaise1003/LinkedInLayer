from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^settings/', include('livesettings.urls')),
    (r'^$', 'linkedinopenerp.layer.views.home', {}, 'home'),
    (r'^home/$', 'linkedinopenerp.layer.views.home', {}, 'home'),
    (r'^error/$', 'linkedinopenerp.layer.views.error', {}, 'error'),
    (r'^auth/linkedin/$', 'linkedinopenerp.layer.views.linkedin_auth', {}, 'linkedin_auth'),
    (r'^auth/linkedin/employee/$', 'linkedinopenerp.layer.views.linkedin_auth_empl', {}, 'linkedin_auth_empl'),
    (r'^auth/linkedin/contact/$', 'linkedinopenerp.layer.views.linkedin_auth_cont', {}, 'linkedin_auth_cont'),
    (r'^auth/linkedin/company/$', 'linkedinopenerp.layer.views.linkedin_auth_comp', {}, 'linkedin_auth_comp'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.STATIC_ROOT}),
    )
