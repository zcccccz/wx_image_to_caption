import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

import requests

from skimage import io

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
    r = requests.post(url, data=data, headers=headers,verify=False)
    image_url = r.json()['file_list'][0]['download_url']
    
    image = io.imread(image_url)
    image_shape = str(image.shape)


    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = JsonResponse({
            'code': 0,
            "data": 'FengFu success!',
            'message':'我已经成功获得图片url!',
            'url':image_url,
            'shape':image_shape,
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