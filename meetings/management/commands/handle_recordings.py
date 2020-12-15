import datetime
import logging
import os
import requests
import tempfile
import wget
import multiprocessing
from django.db.models import Q
from django.conf import settings
from obs import ObsClient
from meetings.models import Meeting, Video

logger = logging.getLogger('log')


def get_recordings(mid):
    """
    查询一个会议的录像信息并返回
    :param mid: 会议ID
    :return: the json-encoded content of a response or none
    """
    url = 'https://api.zoom.us/v2/meetings/{}/recordings'.format(mid)
    headers = {
        'authorization': 'Bearer {}'.format(settings.ZOOM_TOKEN)
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error('get recordings:', response.status_code, response.json()['message'])
        return
    return response.json()


def get_participants(mid):
    """
    查询一个会议的所有参会者
    :param mid: 会议ID
    :return: the json-encoded content of a response or none
    """
    url = 'https://api.zoom.us/v2/past_meetings/{}/participants'.format(mid)
    headers = {
        'authorization': 'Bearer {}'.format(settings.ZOOM_TOKEN)
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        logger.error('get participants:', response.status_code, response.json()['message'])
        return
    return response.json()


def download_recordings(zoom_download_url, mid):
    """
    下载录像视频
    :param zoom_download_url: zoom提供的下载地址
    :param mid: 会议ID
    :return: 下载的文件名
    """
    target_name = mid + '.mp4'
    # 判断/tmp/下有无target_name,如果存在则删掉再下载
    if target_name in os.listdir('/tmp'):
        os.remove('/tmp/{}'.format(target_name))
    r = requests.get(url=zoom_download_url, allow_redirects=False)
    url = r.headers['location']
    tmpdir = tempfile.gettempdir()
    filename = wget.download(url, out=os.path.join(tmpdir, target_name))
    return filename


def download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint, object_key, group_name,
                               obs_client):
    """
    下载、上传录像及后续操作
    :param start: 录像开始时间
    :param end: 录像结束时间
    :param zoom_download_url: zoom录像下载地址
    :param mid: 会议ID
    :param total_size: 文件大小 
    :param video: Video的实例
    :param endpoint: OBS终端节点
    :param object_key: 文件在OBS上的位置
    :param group_name: sig组名
    :param obs_client: ObsClient的实例
    :return: 
    """
    # 下载录像
    filename = download_recordings(zoom_download_url, str(mid))
    logger.info('download file: {}'.format(filename))
    try:
        # 若下载的录像的大小和查询到的total_size相等，则继续
        download_file_size = os.path.getsize(filename)
        logger.info('the size of download file: {}'.format(download_file_size))
        if download_file_size == total_size:
            topic = video.topic
            agenda = video.agenda
            bucketName = os.getenv('OBS_BUCKETNAME', '')
            download_url = 'https://{}.{}/{}?response-content-disposition=attachment'.format(bucketName,
                                                                                             endpoint,
                                                                                             object_key)
            attenders = get_participants(mid)
            # 生成metadata
            metadata = {
                "meeting_id": mid,
                "meeting_topic": topic,
                "sig": group_name,
                "agenda": agenda,
                "record_start": start,
                "record_end": end,
                "download_url": download_url,
                "total_size": total_size,
                "attenders": attenders
            }
            # 上传视频
            try:
                # 断点续传上传文件
                res = obs_client.uploadFile(bucketName=bucketName, objectKey=object_key, uploadFile=filename,
                                            taskNum=10, enableCheckpoint=True, metadata=metadata)
                try:
                    if res['status'] == 200:
                        logger.info('upload file {} successfully'.format(filename))
                        # 更新数据库
                        try:
                            video.update(start=start, end=end, zoom_download_url=zoom_download_url,
                                         download_url=download_url, total_size=total_size,
                                         attenders=attenders)
                            logger.info('update data in database')
                        except Exception as e4:
                            logger.error('fail to update database!', e4)
                except KeyError as e3:
                    logger.error('fail to upload file!', e3)
            except Exception as e2:
                logger.error('upload file error!', e2)
        else:
            # 否则，删除刚下载的文件
            os.remove(filename)
    except FileNotFoundError as e1:
        logger.error(e1)


def run(mid):
    """
    查询Video根据total_size判断是否需要执行后续操作（下载、上传、保存数据）
    :param mid: 会议ID
    :return:
    """
    logger.info('handle recordings: {}'.format(mid))
    video = Video.objects.get(mid=mid)
    # 查询会议的录像信息
    recordings = get_recordings(mid)
    if recordings:
        total_size = recordings['total_size']
        logger.info('total size of the recordings: {}'.format(total_size))
        # 连接obs服务，实例化ObsClient
        access_key_id = os.getenv('ACCESS_KEY_ID', '')
        secret_access_key = os.getenv('SECRET_ACCESS_KEY', '')
        endpoint = os.getenv('OBS_ENDPOINT', '')
        bucketName = 'records'
        try:
            obs_client = ObsClient(access_key_id=access_key_id,
                                   secret_access_key=secret_access_key,
                                   server='https://{}'.format(endpoint))
            logger.info('connect OBS client successfully.')
            objs = obs_client.listObjects(bucketName=bucketName)
            # 预备文件上传路径
            start = recordings['recording_files'][0]['recording_start']
            month = datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S").strftime(
                "%b").lower()
            group_name = video.group_name
            video_name = mid + '.mp4'
            object_key = 'opeueuler/{}/{}/{}/{}'.format(group_name, month, mid, video_name)
            # 收集录像信息待用
            end = recordings['recording_files'][0]['recording_end']
            zoom_download_url = recordings['recording_files'][0]['download_url']
            if not objs['body']['contents']:
                download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint, object_key,
                                           group_name, obs_client)
            for obj in objs['body']['contents']:
                if obj['key'] == object_key and obj['size'] > total_size:
                    pass
                else:
                    download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint,
                                               object_key, group_name, obs_client)
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    meeting_ids = Video.objects.all().values_list('mid', flat=True)
    past_meetings = Meeting.objects.filter(Q(date__gt=str(datetime.datetime.now() - datetime.timedelta(days=2))) &
                                           Q(date__lte=datetime.datetime.now().strftime('%Y-%m-%d')))
    recent_mids = [x for x in meeting_ids if x in past_meetings.values_list('mid', flat=True)]
    pool = multiprocessing.Pool()
    pool.map(run, recent_mids)
    pool.close()
    pool.join()

