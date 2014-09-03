import string
import logging

import random
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import views as auth_views
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from mongoengine.django.auth import User


from . import forms
from api import mongo


logger = logging.getLogger(__name__)


def index(request):
	ctx = {}

	logger.debug('Index requested from IP %s' % request.META.get('REMOTE_ADDR'))

	return render(request, 'pages/index.html', ctx)


@login_required
def settings(request):
	ctx = {
		'user_doc': mongo.db.user.find_one({'username': request.user.username})
	}

	logger.debug('Index requested from IP %s' % request.META.get('REMOTE_ADDR'))

	return render(request, 'pages/settings.html', ctx)


def register(request):
	logger.debug('Register requested from IP %s' % request.META.get('REMOTE_ADDR'))

	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('web.index'))

	if request.method == 'GET':
		ctx = {'user': request.user, 'form': forms.RegisterForm(), }

		return render(request, 'pages/register.html', ctx)

	if request.method == 'POST':
		form = forms.RegisterForm(request.POST)
		if not form.is_valid():
			ctx = {'form': form, }

			return render(request, 'pages/register.html', ctx)

		else:
			new_user = User()
			random_username = ''.join(random.sample(string.ascii_lowercase * 30, 20))
			new_user.username = random_username
			new_user.email = form.cleaned_data['email']
			new_user.is_active = True
			new_user.is_staff = False
			new_user.is_superuser = False
			new_user.set_password(form.cleaned_data['password'])
			new_user.save()

			user_doc = mongo.db.user.find_one({'username': new_user.username})
			user_doc['writing_api_key'] = ''.join(random.sample(string.ascii_lowercase * 30, 20))
			user_doc['reading_api_key'] = ''.join(random.sample(string.ascii_lowercase * 30, 20))
			del user_doc['_id']
			mongo.db.user.update({'username': new_user.username}, {'$set': user_doc})

			logger.info('New user registered with email: %s' % new_user.email)

			# log in
			auth_login(request, authenticate(username=random_username, password=form.cleaned_data.get("password")))

			return HttpResponseRedirect(reverse('web.settings'))


def login(request):
	ctx = {}

	logger.debug('Login requested from IP %s' % request.META.get('REMOTE_ADDR'))

	# Redirect to index if user is logged in or display login otherwise
	if request.user and request.user.is_authenticated():
		return HttpResponseRedirect(reverse('web.index'))
	return auth_views.login(request, template_name='pages/login.html', authentication_form=forms.LoginForm,
		extra_context=ctx)


# 4 views for password reset:
# - password_reset sends the mail
# - password_reset_done shows a success message for the above
# - password_reset_confirm checks the link the user clicked and prompts for a new password
# - password_reset_complete shows a success message for the above

@csrf_protect
def password_reset(request):
	if request.method == "POST":
		form = forms.PasswordResetForm(request.POST)
		if form.is_valid():
			print(form.cleaned_data)
			print(form.cleaned_data['email'])
			opts = {
				'use_https': request.is_secure(),
			}
			form.save(**opts)
			return HttpResponseRedirect(reverse('web.password_reset_sent'))
	else:
		form = forms.PasswordResetForm()
	ctx = {'form': form}
	return render(request, 'pages/password_reset.html', ctx)


def password_reset_sent(request):
	ctx = {}
	return render(request, 'pages/password_reset_sent.html', ctx)


# Doesn't need csrf_protect since no-one can guess the URL
@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None):
	"""
	View that checks the hash in a password reset link and presents a
	form for entering a new password.
	"""
	assert uidb64 is not None and token is not None  # checked by URLconf
	post_reset_redirect = reverse('web.password_reset_done')
	try:
		uid = urlsafe_base64_decode(uidb64).decode('utf-8')
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None and default_token_generator.check_token(user, token):
		validlink = True
		if request.method == 'POST':
			form = forms.SetPasswordForm(user, request.POST)
			if form.is_valid():
				form.save()
				return HttpResponseRedirect(post_reset_redirect)
		else:
			form = forms.SetPasswordForm(None)
	else:
		validlink = False
		form = None
	ctx = {'form': form, 'validlink': validlink, }
	return render(request, 'pages/password_reset_confirm.html', ctx)


def password_reset_done(request):
	ctx = {'login_url': reverse('web.login')}
	return render(request, 'pages/password_reset_done.html', ctx)
