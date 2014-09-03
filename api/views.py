import json
import logging


from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from bson.objectid import ObjectId


from . import decorators, encoders, mongo


logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(['GET', 'POST', 'DELETE', 'OPTIONS'])
@decorators.methods
def data(request):
	if request.method == 'GET':
		return data_get(request)
	elif request.method == 'POST':
		return data_post(request)
	elif request.method == 'DELETE':
		return data_delete(request)
	elif request.method == 'OPTIONS':
		return data_options(request)


@decorators.cors
def data_get(request):
	reading_key = request.GET.get('readingKey')

	if reading_key is None:
		return HttpResponseForbidden('No api key')

	existing_user_count = mongo.db.user.find({'reading_api_key': reading_key}).count()
	if existing_user_count == 0:
		return HttpResponseNotFound('No user with this api key')

	doc_id = request.GET.get('documentId')

	if doc_id is not None:
		doc = mongo.db.documents.find_one({'_id': ObjectId(doc_id), 'readingKey': reading_key})

		return HttpResponse(json.dumps({'status': 'ok', 'document': json.loads(doc.get('data'))}, cls=encoders.DBJSONEncoder), content_type='application/json')
	else:
		docs = [json.loads(doc.get('data')) for doc in mongo.db.documents.find({'readingKey': reading_key})]

		return HttpResponse(json.dumps({'status': 'ok', 'documents': docs}, cls=encoders.DBJSONEncoder), content_type='application/json')


@decorators.cors
def data_post(request):
	writing_key = request.POST.get('writingKey')

	if writing_key is None:
		return HttpResponseForbidden('No api key')

	existing_user = mongo.db.user.find_one({'writing_api_key': writing_key})
	if existing_user is None:
		return HttpResponseNotFound('No user with this api key')

	doc = request.POST.get('document')
	doc_id = request.POST.get('documentId')

	try:
		json.loads(doc)
	except:
		return HttpResponseBadRequest('Document is not JSON')

	if len(doc) > 1000000:
		return HttpResponseBadRequest('Document too large')

	if doc_id:
		existing_doc = mongo.db.documents.find_one({'_id': ObjectId(doc_id), 'readingKey': existing_user.get('reading_api_key')})

		if existing_doc is None:
			return HttpResponseNotFound('No document with supplied id')

		existing_doc['data'] = doc
		del existing_doc['_id']

		mongo.db.documents.update({'_id': ObjectId(doc_id)}, {'$set': existing_doc})
	else:
		existing_docs_count = mongo.db.documents.find({'readingKey': existing_user.get('reading_api_key')}).count()

		if existing_docs_count >= 5:
			return HttpResponseBadRequest('You have 5 documents stored already')

		new_doc = {
			'readingKey': existing_user.get('reading_api_key'),
			'data': doc
		}

		mongo.db.documents.insert(new_doc)

	return HttpResponse(json.dumps({'status': 'ok'}, cls=encoders.DBJSONEncoder), content_type='application/json')


@decorators.cors
def data_delete(request):
	writing_key = request.DELETE.get('writingKey')

	if writing_key is None:
		return HttpResponseForbidden('No api key')

	existing_user = mongo.db.user.find_one({'writing_api_key': writing_key})
	if existing_user is None:
		return HttpResponseNotFound('No user with this api key')

	reading_key = existing_user.get('reading_api_key')

	doc_id = request.DELETE.get('documentId')

	if doc_id is not None:
		mongo.db.documents.remove({'_id': ObjectId(doc_id), 'readingKey': reading_key})
	else:
		mongo.db.documents.remove({'readingKey': reading_key})

	return HttpResponse(json.dumps({'status': 'ok'}, cls=encoders.DBJSONEncoder), content_type='application/json')


@decorators.cors
def data_options(request):
	return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')

