import requests
import logging
import sys
import json
import tempfile
import os
from obs import ObsClient

logger = logging.getLogger('log')


def get_token(appid, secret):
    url = 'https://api.weixin.qq.com/cgi-bin/token?appid={}&secret={}&grant_type=client_credential'.format(appid,
                                                                                                           secret)
    r = requests.get(url)
    if r.status_code == 200:
        try:
            access_token = r.json()['access_token']
            return access_token
        except KeyError as e:
            logger.error(e)
    else:
        logger.error(r.json())
        logger.error('fail to get access_token,exit.')
        sys.exit(1)


def gene_code_img(appid, secret, activity_id):
    wx_token = get_token(appid, secret)
    url = 'https://api.weixin.qq.com/wxa/getwxacodeunlimit?access_token={}'.format(wx_token)
    data = {
        "scene": activity_id
        "page": "package-events/events/event-detail"
    }
    res = requests.post(url, data=json.dumps(data))
    if res.status_code != 200:
        logger.error(r.json())
        logger.error('fail to get QR code')
        sys.exit(1)
    return res.content


def save_temp_img(content):
    tmpdir = tempfile.gettempdir()
    tmp_file = os.path.join(tmpdir, 'tmp.jpeg')
    with open(tmp_file, 'wb') as f:
        f.write(content)
    return tmp_file


def upload_to_obs(tmp_file, activity_id):
    access_key_id = os.getenv('ACCESS_KEY_ID', '')
    secret_access_key = os.getenv('SECRET_ACCESS_KEY', '')
    endpoint = os.getenv('OBS_ENDPOINT', '')
    bucketName = os.getenv('OBS_BUCKETNAME_SECOND', '')
    if not access_key_id or not secret_access_key or not endpoint or not bucketName:
        logger.error('losing required arguments for ObsClient')
        sys.exit(1)
    obs_client = ObsClient(access_key_id=access_key_id,
                           secret_access_key=secret_access_key,
                           server='https://{}'.format(endpoint))
    object_key = 'openeuler/miniprogram/activity/{}/wx_code.jpeg'.format(activity_id)
    obs_client.uploadFile(bucketName=bucketName, objectKey=object_key, uploadFile=tmp_file, taskNum=10, enableCheckpoint=True)
    img_url = 'https://{}.{}/{}'.format(bucketName, endpoint, object_key)
    return img_url


def run(appid, secret, activity_id):
    content = gene_code_img(appid, secret, activity_id)
    tmp_file = save_temp_img(content)
    img_url = upload_to_obs(tmp_file, activity_id)
    return img_url
