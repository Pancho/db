from django.conf.urls import patterns, url


urlpatterns = patterns('api.views',
	# DATA API
	url(r'^data/$', 'data', name='api.data'),
)