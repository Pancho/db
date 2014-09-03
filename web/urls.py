from django.conf.urls import patterns, url


urlpatterns = patterns('web.views',
	# Login
	url(r'^login/$', 'login', name='web.login'),
	# Register
	url(r'^register/$', 'register', name='web.register'),
	# Index
	url(r'^$', 'index', name='web.index'),
	# Settings
	url(r'^settings/$', 'settings', name='web.settings'),
	# Password reset chain
	url(r'^password/reset/$', 'password_reset', name='web.password_reset'),
	url(r'^password/reset/sent/$', 'password_reset_sent', name='web.password_reset_sent'),
	url(r'^password/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', 'password_reset_confirm', name='web.password_reset_confirm'),
	url(r'^password/reset/done/$', 'password_reset_done', name='web.password_reset_done'),
)