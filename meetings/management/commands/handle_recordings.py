import datetime
import logging
import os
import requests
import tempfile
import wget
from multiprocessing.dummy import Pool as ThreadPool
from django.db.models import Q
from django.conf import settings
from obs import ObsClient
from meetings.models import Meeting, Video
from django.core.management.base import BaseCommand

logger = logging.getLogger('log')


class Command(BaseCommand):
    def handle(self, *args, **options):
        meeting_ids = Video.objects.all().values_list('mid', flat=True)
        past_meetings = Meeting.objects.filter(Q(date__gt=str(datetime.datetime.now() - datetime.timedelta(days=2))) &
                                               Q(date__lte=datetime.datetime.now().strftime('%Y-%m-%d')))
        recent_mids = [x for x in meeting_ids if x in past_meetings.values_list('mid', flat=True)]
        pool = ThreadPool()
        pool.map(run, recent_mids)
        pool.close()
        pool.join()
        logger.info('All done')


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
        logger.error('mid: {}, get recordings:'.format(mid), response.status_code, response.json()['message'])
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
        logger.error('mid: {}, get participants:'.format(mid), response.status_code, response.json()['message'])
        return
    return response.json()['participants']


def download_recordings(zoom_download_url, mid):
    """
    下载录像视频
    :param zoom_download_url: zoom提供的下载地址
    :param mid: 会议ID
    :return: 下载的文件名
    """
    tmpdir = tempfile.gettempdir()
    target_name = mid + '.mp4'
    # 判断/tmp/下有无target_name,如果存在则删掉再下载
    if target_name in os.listdir(tmpdir):
        os.remove(os.path.join(tmpdir, target_name))
    r = requests.get(url=zoom_download_url, allow_redirects=False)
    url = r.headers['location']
    # tmpdir = tempfile.gettempdir()
    filename = wget.download(url, out=os.path.join(tmpdir, target_name))
    return filename


def generate_cover(mid, topic, group_name, date, filename):
    """生成封面"""
    html_path = filename.replace('.mp4', '.html')
    image_path = filename.replace('.mp4', '.png')
    f = open(html_path, 'w')
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Title</title>
    </head>
    <body>
    <div style="display: inline-block; width: 63rem; height: 42rem;text-align: center">
        <h1 style="margin-top: 10rem">{0}</h1>
        <h4 style="margin-top: 12rem">兴趣组：{1}</h4>
        <h4>时间：{2}</h4>
        <img src="openeuler.jpg" alt="openEuler" />
    </div>
    </body>
    </html>
    """.format(topic, group_name, date)
    f.write(content)
    f.close()
    os.system("cp static/img/openeuler.jpg {}".format(os.path.dirname(filename)))
    os.system("wkhtmltoimage --enable-local-file-access {} {}".format(html_path, image_path))
    logger.info("meeting {}: 生成封面".format(mid))


def upload_cover(filename, obs_client, bucketName, cover_path):
    """OBS上传封面"""
    res = obs_client.uploadFile(bucketName=bucketName, objectKey=cover_path, uploadFile=filename.replace('.mp4', '.png'),
                                taskNum=10, enableCheckpoint=True)
    return res


def download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint, object_key,
                               group_name,
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
    print()
    logger.info('meeting {}: 从OBS下载{}'.format(mid, filename))
    try:
        # 若下载的录像的大小和查询到的total_size相等，则继续
        download_file_size = os.path.getsize(filename)
        logger.info('meeting {}: 下载的文件大小为{}'.format(mid, download_file_size))
        if download_file_size == total_size:
            topic = video.topic
            agenda = video.agenda
            community = video.community
            bucketName = os.getenv('OBS_BUCKETNAME', '')
            if not bucketName:
                logger.error('mid: {}, bucketName required'.format(mid))
                return
            download_url = 'https://{}.{}/{}?response-content-disposition=attachment'.format(bucketName,
                                                                                             endpoint,
                                                                                             object_key)
            attenders = get_participants(mid)
            # 生成metadata
            metadata = {
                "meeting_id": mid,
                "meeting_topic": topic,
                "community": community,
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
                        logger.info('meeting {}: OBS视频上传成功'.format(mid, filename))
                        # 生成封面
                        date = datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''),
                                                          "%Y-%m-%d %H:%M:%S").strftime(
                            '%Y-%m-%d')
                        generate_cover(mid, topic, group_name, date, filename)
                        # 上传封面
                        cover_path = res['body']['key'].replace('.mp4', '.png')
                        res2 = upload_cover(filename, obs_client, bucketName, cover_path)
                        if res2['status'] == 200:
                            logger.info('meeting {}: OBS封面上传成功'.format(mid))
                            try:
                                Video.objects.filter(mid=mid).update(start=start, end=end,
                                                                     zoom_download_url=zoom_download_url,
                                                                     download_url=download_url, total_size=total_size,
                                                                     attenders=attenders)
                                logger.info('meeting {}: 更新数据库'.format(mid))
                                # 删除临时文件
                                os.remove(filename)
                                logger.info('meeting {}: 移除临时文件{}'.format(mid, filename))
                                os.remove(filename.replace('.mp4', '.html'))
                                logger.info(
                                    'meeting {}: 移除临时文件{}'.format(mid, filename.replace('.mp4', '.html')))
                                os.remove(filename.replace('.mp4', '.png'))
                                logger.info(
                                    'meeting {}: 移除临时文件{}'.format(mid, filename.replace('.mp4', '.png')))
                                return topic, filename
                            except Exception as e4:
                                logger.error('meeting {}: fail to update database!'.format(mid), e4)
                except KeyError as e3:
                    logger.error('meeting {}: fail to upload file!'.format(mid), e3)
            except Exception as e2:
                logger.error('meeting {}: upload file error!'.format(mid), e2)
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
    logger.info('meeting {}: 开始处理'.format(mid))
    video = Video.objects.get(mid=mid)
    # 查询会议的录像信息
    recordings = get_recordings(mid)
    if recordings:
        total_size = recordings['total_size']
        logger.info('meeting {}: 录像文件的总大小为{}'.format(mid, total_size))
        # 连接obs服务，实例化ObsClient
        access_key_id = os.getenv('ACCESS_KEY_ID', '')
        secret_access_key = os.getenv('SECRET_ACCESS_KEY', '')
        endpoint = os.getenv('OBS_ENDPOINT', '')
        bucketName = os.getenv('OBS_BUCKETNAME', '')
        if not (access_key_id and secret_access_key and endpoint and bucketName):
            logger.error('losing required arguments for ObsClient')
            return
        try:
            obs_client = ObsClient(access_key_id=access_key_id,
                                   secret_access_key=secret_access_key,
                                   server='https://{}'.format(endpoint))
            objs = obs_client.listObjects(bucketName=bucketName)
            # 预备文件上传路径
            start = recordings['recording_files'][0]['recording_start']
            month = datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S").strftime(
                "%b").lower()
            group_name = video.group_name
            video_name = mid + '.mp4'
            object_key = 'openeuler/{}/{}/{}/{}'.format(group_name, month, mid, video_name)
            logger.info('meeting {}: object_key is {}'.format(mid, object_key))
            # 收集录像信息待用
            end = recordings['recording_files'][0]['recording_end']
            zoom_download_url = recordings['recording_files'][0]['download_url']
            if not objs['body']['contents']:
                logger.info('meeting {}: OBS无存储对象，开始下载视频'.format(mid))
                topic, filename = download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint, object_key,
                                           group_name, obs_client)
                return {"mid": mid, "topic": topic, "filename": filename}
            else:
                key_size_map = {x['key']: x['size'] for x in objs['body']['contents']}
                if object_key not in key_size_map.keys():
                    logger.info('meeting {}: OBS存储服务中无此对象，开始下载视频'.format(mid))
                    topic, filename = download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint,
                                               object_key,
                                               group_name, obs_client)
                    return {"mid": mid, "topic": topic, "filename": filename}
                elif object_key in key_size_map.keys() and key_size_map[object_key] >= total_size:
                    logger.info('meeting {}: OBS存储服务中已存在该对象且无需替换'.format(mid))
                    return
                else:
                    logger.info('meeting {}: OBS存储服务中该对象需要替换，开始下载视频'.format(mid))
                    topic, filename = download_upload_recordings(start, end, zoom_download_url, mid, total_size, video, endpoint,
                                               object_key, group_name, obs_client)
                    return {"mid": mid, "topic": topic, "filename": filename}
        except Exception as e:
            logger.error(e)
