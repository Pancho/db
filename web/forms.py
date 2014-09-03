import logging


from django import forms
from django.http import Http404
from django.contrib.auth import authenticate
from django.contrib.auth import forms as authforms
from django.core.mail.message import EmailMultiAlternatives
from django.template import loader
from django.template.context import Context
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from mongoengine.django.auth import User


from db import settings
from api import mongo


logger = logging.getLogger(__name__)


class RegisterForm(forms.Form):
	email = forms.EmailField(error_messages={'invalid': 'Enter your e-mail', 'required': 'This field is mandatory'}, label='e-mail', widget=forms.TextInput(attrs={'type': 'email'}))
	password = forms.CharField(error_messages={'required': 'Enter your password'}, max_length=128, label='Password', widget=forms.PasswordInput)

	def clean(self):
		if mongo.db.user.find({'email': self.cleaned_data['email']}).count() > 0:
			raise forms.ValidationError('User with this email is already registered')

		return self.cleaned_data


class LoginForm(forms.Form):
	email = forms.EmailField(error_messages={'invalid': 'Enter your e-mail', 'required': 'This field is mandatory'}, label='e-mail', widget=forms.TextInput(attrs={'type': 'email', 'required': 'required'}))
	password = forms.CharField(error_messages={'required': 'Enter your password'}, max_length=128, label='Password', widget=forms.PasswordInput(attrs={'required': 'required'}))

	def __init__(self, request=None, *args, **kwargs):
		self.request = request
		self.authenticated_user = None
		super(LoginForm, self).__init__(*args, **kwargs)

	def clean(self):
		email = self.cleaned_data.get("email")
		password = self.cleaned_data.get("password")

		user = mongo.db.user.find_one({'email': email})

		if user is None:
			raise forms.ValidationError('Email and password don\'t match.')

		username = user.get('username')

		if username and password:
			self.authenticated_user = authenticate(username=username, password=password)
			if self.authenticated_user is None:
				raise forms.ValidationError('Email and password don\'t match.')
			elif not self.authenticated_user.is_active:
				raise forms.ValidationError('User account isn\'t active')

		return self.cleaned_data

	def get_user(self):
		return self.authenticated_user


class PasswordResetForm(forms.Form):
	email = forms.EmailField(error_messages={'invalid': 'Enter your e-mail', 'required': 'This field is mandatory'}, label='e-mail', widget=forms.TextInput(attrs={'type': 'email', 'required': 'required'}))

	def clean(self):
		try:
			User.objects.get(email=self.cleaned_data['email'])
		except User.DoesNotExist:
			raise forms.ValidationError('No user registered with that email')

		return self.cleaned_data

	def save(self, use_https=False):
		user = User.objects.get(email=self.cleaned_data['email'])

		ctx = Context({
			'email': user.email,
			'domain': settings.SITE.get('domain'),
			'site_name': settings.SITE.get('name'),
			'uid': urlsafe_base64_encode(bytes(str(user.pk), 'utf-8')),
			'user': user,
			'token': default_token_generator.make_token(user),
			'protocol': use_https and 'https' or 'http',
		})

		text_body = loader.get_template('email/email_password_reset.txt').render(ctx)
		html_body = loader.get_template('email/email_password_reset.html').render(ctx)
		try:
			bcc = []
			if hasattr(settings, 'EMAIL_LOG'):
				bcc.append(settings.EMAIL_LOG)
			email = EmailMultiAlternatives('Password reset for db.panco.si', text_body, 'password-reset@panco.si', [user.email], bcc)
			email.attach_alternative(html_body, 'text/html')
			email.send()
		except Exception as ex:
			logger.critical('Could not send email for password reset to %s | %s' % (user.email, ex))


class SetPasswordForm(authforms.SetPasswordForm):
	new_password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'required': 'required'}))
	new_password2 = forms.CharField(label="Password Repeated", widget=forms.PasswordInput(attrs={'required': 'required'}))