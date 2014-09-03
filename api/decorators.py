from django.http.multipartparser import MultiPartParser


ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age'


def cors(function):
	def wrapper(request, *args, **kwargs):
		response = function(request, *args, **kwargs)

		response[ACCESS_CONTROL_ALLOW_ORIGIN] = '*'
		response[ACCESS_CONTROL_MAX_AGE] = 86400
		response[ACCESS_CONTROL_ALLOW_METHODS] = 'GET, POST, DELETE, OPTIONS'
		response[ACCESS_CONTROL_ALLOW_HEADERS] = 'x-requested-with, content-type, accept, origin, authorization, x-csrftoken'
		response[ACCESS_CONTROL_ALLOW_CREDENTIALS] = 'false'
		response[ACCESS_CONTROL_EXPOSE_HEADERS] = ''

		return response

	return wrapper


def methods(function):
	def wrapper(request, *args, **kwargs):

		# Update the query dicts only if it's DELETE
		if request.method == 'DELETE':
			parser = MultiPartParser(request.META, request, [], request.encoding)  # We don't need anything special here, we just want to read a couple of parameters here
			query_dict, files = parser.parse()  # And we don't need files, as files are never processed even if sent
			request.DELETE = query_dict

		return function(request, *args, **kwargs)
	return wrapper