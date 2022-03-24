# 从数据库读取模型
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import logging
import requests
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

r = requests.get('http://api.weixin.qq.com/_/cos/getauth')

secret_id = r.json()["TmpSecretId"]
secret_key = r.json()["TmpSecretKey"]   
region = 'ap-shanghai'      
token = r.json()["Token"]
scheme = 'https'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
response = client.download_file(
    Bucket='7072-prod-1gxq0vrt5f11b56e-1310101813',
    Key='/models/bua-d2-frcn-r101.pth',
    DestFilePath='bottom_up_attention/bua-d2-frcn-r101.pth'
)
response = client.download_file(
    Bucket='7072-prod-1gxq0vrt5f11b56e-1310101813',
    Key='/models/meshed_memory_transformer.pth',
    DestFilePath='meshed_memory_transformer/meshed_memory_transformer.pth'
)
