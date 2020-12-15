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
from multiprocessing.dummy import Pool as ThreadPool

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
        os.system('rm /tmp/{}'.format(target_name))
    r = requests.get(url=zoom_download_url, allow_redirects=False)
    url = r.headers['location']
    tmpdir = tempfile.gettempdir()
    filename = wget.download(url, out=os.path.join(tmpdir, target_name))
    return filename


def run(mid):
    video = Video.objects.get(mid=mid)

    # 查询会议的录像信息
    recordings = get_recordings(mid)
    if recordings:
        total_size = recordings['total_size']

        # 数据库中video的total_size存在且小于total_size,或video的total_size不存在，则继续操作
        if (video.total_size and video.total_size < total_size) or not video.total_size:
            # 收集录像信息待用
            start = recordings['recording_files'][0]['recording_start']
            end = recordings['recording_files'][0]['recording_end']
            zoom_download_url = recordings['recording_files'][0]['download_url']

            # 1.预备文件上传路径
            month = datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S").strftime(
                "%b").lower()
            group_name = video.group_name
            video_name = mid + '.mp4'
            objectKey = 'opeueuler/{}/{}/{}/{}'.format(group_name, month, mid, video_name)
            # 2。连接obs服务，实例化ObsClient
            obsClient = ObsClient(access_key_id='OHHM0K0A3VR5CJJ8R4OY',
                                  secret_access_key='K4Z1LaE3kGrNklDa9oDWPlrk0qQ5Q5XUkyEza6rR',
                                  server='https://obs.cn-north-4.myhuaweicloud.com')
            # 3. 列举桶内对象
            bucketName = 'records'
            objs = obsClient.listObjects(bucketName=bucketName)
            keys = [x['key'] for x in objs['body']['contents']]
            # 4. 判断obs服务上是否存在objectKey的文件，存在则删除obs上的对象
            if objectKey in keys:
                obsClient.deleteObject(bucketName=bucketName, objectKey=objectKey)

            # 下载录像
            filename = download_recordings(zoom_download_url, str(mid))
            try:
                # 若下载的录像的大小和查询到的total_size相等，则继续
                if os.path.getsize(filename) == total_size:
                    topic = video.topic
                    agenda = video.agenda
                    download_url = 'https://records.obs.cn-north-4.myhuaweicloud.com/{}' \
                                   '?response-content-disposition=attachment'.format(objectKey)
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
                        res = obsClient.uploadFile(bucketName=bucketName, objectKey=objectKey, uploadFile=filename,
                                                   taskNum=10, enableCheckpoint=True, metadata=metadata)
                        try:
                            if res['status'] == 200:
                                # 更新数据库
                                video.update(start=start, end=end, zoom_download_url=zoom_download_url,
                                             download_url=download_url, total_size=total_size, attenders=attenders)
                        except KeyError as e3:
                            logger.error(e3)
                    except Exception as e2:
                        logger.error(e2)
                else:
                    # 否则，删除刚下载的文件
                    os.system('rm {}'.format(filename))
            except FileNotFoundError as e:
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

