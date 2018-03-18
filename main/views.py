from django.shortcuts import render

# Create your views here.
from uuid import uuid4
from urllib.parse import urlparse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST, require_http_methods
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from scrapyd_api import ScrapydAPI
# from main.utils import URLUtil
from main.models import ScrapyUnit


# providing url for scrapy api
scrapyd = ScrapydAPI('http://localhost:6800')

def is_valid_url(url):
    validate = URLValidator
    try:
        validate(url)
    except ValidationError:
        return False
    return True


@csrf_exempt
@require_http_methods(['POST','GET'])  # limiting only get and post
def crawl(request):
    # New crawl request will be a POST request
    if request.method = 'POST':
        url = request.POST.get('url',None) # url to be crawled
        if not url:
            return JsonResponse({'error':'Missing args'})
        
        if not is_valid_url(url):
            return JsonResponse({'error':'URL is invalid'})
        
        domain = urlparse(url).netloc # parse url and fetch the domain
        unique_id = str(uuid4())

        # settings for scrapy
        settings = {
            'unique_id': unique_id, # unique id for each crawl
            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }

        # scheduling the new crawling task for scrapyd
        # ID returned from scheduler can be used to check task's status
        task = scrapyd.schedule('default','icrawler',
                                settings=settings, url=url, domain=domain)
        
        return JsonResponse({'task_id':task, 'unique_id':unique_id, 'status':'started'})

    # results can be fetched from the client side with a GET request
    elif request.method = 'GET':
        # checking if crawling is completed and fetching data
        task_id = request.GET.get('task_id', None)
        unique_id = request.GET.get('unique_id', None)
        
        if not task_id or not unique_id:
            return JsonResponse({'error':'Missing args'})
        
        status = scrapyd.job_status('default', task_id)
        if status == 'finished':
            try:
                item = ScrapyUnit.objects.get(unique_id=unique_id)
                return JsonResponse({'data':item.to_dict['data']})
            except Exception as e:
                return JsonResponse({'error':str(e)})
        else:
            return JsonResponse({'status': status})
