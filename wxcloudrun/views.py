import json
import logging
from django.http import JsonResponse
from django.shortcuts import render
import requests


logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def zcztest(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    fID = body['fID']
    url = 'https://api.weixin.qq.com/tcb/batchdownloadfile'
    env = 'prod-1gxq0vrt5f11b56e'
    file_list = [
        {
        "fileid":fID,
        "max_age":7200,
        }
    ]
    data = json.dumps({
        'env':env,
        'file_list':file_list,
    })
    headers = {'Content-Type': 'application/json'}
    requests.packages.urllib3.disable_warnings()
    r = requests.post(url, data=data, headers=headers,verify=False)
    image_url = r.json()['file_list'][0]['download_url']

    ali_url = 'http://106.15.238.138/api/zczrequest'
    image_link = image_url
    data = json.dumps({
        'image_link':image_link
    })
    headers = {'Content-Type': 'application/json'}
    requests.packages.urllib3.disable_warnings()
    r = requests.post(ali_url, data=data, headers=headers,verify=False)
    caption = r.json()['caption']
    caption = caption.capitalize()


    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = JsonResponse({
            'code': 0,
            "data": 'FengFu success!',
            'caption':caption,
            },
            json_dumps_params={'ensure_ascii': False})
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp



def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """
    return JsonResponse({'code': 0, "data": 10},
                    json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))
    return JsonResponse({'code': 0, "data": 10},
                    json_dumps_params={'ensure_ascii': False})