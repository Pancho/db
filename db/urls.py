from django.conf.urls import patterns, include, url


from db import settings
from web import forms


urlpatterns = patterns('',
	# WEB
	(r'', include('web.urls')),

	# API
	(r'^api/', include('api.urls')),

	# STATIC CONTENT
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

# Logout (Djnago's)
urlpatterns += patterns('django.contrib.auth.views',
	url(r'^logout/$', 'logout_then_login', name='db.logout'),
)
