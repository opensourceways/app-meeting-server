import datetime
import logging
import os
import requests
import tempfile
import wget
from django.db.models import Q
from django.conf import settings
from obs import ObsClient
from django.core.management.base import BaseCommand
from meetings.models import Meeting, Video, Record
from multiprocessing.dummy import Pool as ThreadPool
from meetings.utils.html_template import cover_content

logger = logging.getLogger('log')


class Command(BaseCommand):
    def handle(self, *args, **options):
        meeting_ids = Video.objects.all().values_list('mid', flat=True)
        past_meetings = Meeting.objects.filter(is_delete=0).filter(
            Q(date__gt=str(datetime.datetime.now() - datetime.timedelta(days=7))) &
            Q(date__lte=datetime.datetime.now().strftime('%Y-%m-%d')))
        recent_mids = [x for x in meeting_ids if x in list(past_meetings.values_list('mid', flat=True))]
        logger.info('meeting_ids: {}'.format(list(meeting_ids)))
        logger.info('mids of past_meetings: {}'.format(list(past_meetings.values_list('mid', flat=True))))
        logger.info('recent_mids: {}'.format(recent_mids))
        pool = ThreadPool()
        pool.map(run, recent_mids)
        pool.close()
        pool.join()
        logger.info('All done')


def get_recordings(mid):
    """
    查询一个host下昨日至今日(默认)的所有录像
    :param mid: 会议ID
    :return: the json-encoded content of a response or none
    """
    host_id = Meeting.objects.get(mid=mid).host_id
    url = 'https://api.zoom.us/v2/users/{}/recordings'.format(host_id)
    headers = {
        'authorization': 'Bearer {}'.format(settings.ZOOM_TOKEN)
    }
    params = {
        'from': (datetime.datetime.now() - datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
        'page_size': 50
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        logger.error('get recordings: {} {}'.format(response.status_code, response.json()['message']))
        return
    mids = [x['id'] for x in response.json()['meetings']]
    if mids.count(int(mid)) == 0:
        logger.info('meeting {}: no recordings yet'.format(mid))
        return
    if mids.count(int(mid)) == 1:
        record = list(filter(lambda x:x if x['id'] == int(mid) else None, response.json()['meetings']))[0]
        return record
    if mids.count(int(mid)) > 1:
        records = list(filter(lambda x: x if x['id'] == int(mid) else None, response.json()['meetings']))
        max_size = max([x['total_size'] for x in records])
        record = list(filter(lambda x: x if x['total_size'] == max_size else None, response.json()['meetings']))[0]
        return record


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
        logger.error('mid: {}, get participants {} {}:'.format(mid, response.status_code, response.json()['message']))
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
    filename = wget.download(url, out=os.path.join(tmpdir, target_name))
    return filename


def generate_cover(mid, topic, group_name, date, filename, start_time, end_time):
    """生成封面"""
    html_path = filename.replace('.mp4', '.html')
    image_path = filename.replace('.mp4', '.png')
    f = open(html_path, 'w')
    content = cover_content(topic, group_name, date, start_time, end_time)
    f.write(content)
    f.close()
    os.system("cp meetings/images/cover.png {}".format(os.path.dirname(filename)))
    os.system("wkhtmltoimage --enable-local-file-access {} {}".format(html_path, image_path))
    logger.info("meeting {}: 生成封面".format(mid))
    os.remove(os.path.join(os.path.dirname(filename), 'cover.png'))


def upload_cover(filename, obs_client, bucketName, cover_path):
    """OBS上传封面"""
    res = obs_client.uploadFile(bucketName=bucketName, objectKey=cover_path,
                                uploadFile=filename.replace('.mp4', '.png'),
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
    logger.info('meeting {}: 从OBS下载视频，本地保存为{}'.format(mid, filename))
    try:
        # 若下载录像的大小和total_size相等，则继续
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
                "total_size": download_file_size,
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
                        date = (datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''),
                                                           "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                            hours=8)).strftime('%Y-%m-%d')
                        start_time = (datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''),
                                                                 "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                            hours=8)).strftime('%H:%M')
                        end_time = (datetime.datetime.strptime(end.replace('T', ' ').replace('Z', ''),
                                                               "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                            hours=8)).strftime('%H:%M')
                        generate_cover(mid, topic, group_name, date, filename, start_time, end_time)
                        # 上传封面
                        cover_path = res['body']['key'].replace('.mp4', '.png')
                        res2 = upload_cover(filename, obs_client, bucketName, cover_path)
                        if res2['status'] == 200:
                            logger.info('meeting {}: OBS封面上传成功'.format(mid))
                            try:
                                Video.objects.filter(mid=mid).update(start=start,
                                                                     end=end,
                                                                     total_size=total_size,
                                                                     attenders=attenders,
                                                                     download_url=download_url)
                                url = download_url.split('?')[0]
                                if Record.objects.filter(mid=mid, platform='obs'):
                                    Record.objects.filter(mid=mid, platform='obs').update(
                                        url=url, thumbnail=url.replace('.mp4', '.png'))
                                else:
                                    Record.objects.create(mid=mid, platform='obs', url=url,
                                                          thumbnail=url.replace('.mp4', '.png'))
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
                                logger.error('meeting {}: fail to update database! {}'.format(mid, e4))
                except KeyError as e3:
                    logger.error('meeting {}: fail to upload file! {}'.format(mid, e3))
            except Exception as e2:
                logger.error('meeting {}: upload file error! {}'.format(mid, e2))
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
        recordings_list = list(filter(lambda x: x if x['file_extension'] == 'MP4' else None, recordings['recording_files']))
        if len(recordings_list) == 0:
            logger.info('meeting {}: 正在录制中'.format(mid))
            return
        if len(recordings_list) > 1:
            max_size = max([x['file_size'] for x in recordings_list])
            for recording in recordings_list:
                if recording['file_size'] != max_size:
                    recordings_list.remove(recording)
        total_size = recordings_list[0]['file_size']
        logger.info('meeting {}: 录像文件的总大小为{}'.format(mid, total_size))
        # 如果文件过小，则视为无效录像
        if total_size < 1024 * 1024 * 10:
            logger.info('meeting {}: 文件过小，不予操作'.format(mid))
        else:
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
                start = recordings_list[0]['recording_start']
                month = datetime.datetime.strptime(start.replace('T', ' ').replace('Z', ''), "%Y-%m-%d %H:%M:%S").strftime(
                    "%b").lower()
                group_name = video.group_name
                video_name = mid + '.mp4'
                object_key = 'openeuler/{}/{}/{}/{}'.format(group_name, month, mid, video_name)
                logger.info('meeting {}: object_key is {}'.format(mid, object_key))
                # 收集录像信息待用
                end = recordings_list[0]['recording_end']
                zoom_download_url = recordings_list[0]['download_url']
                if not objs['body']['contents']:
                    logger.info('meeting {}: OBS无存储对象，开始下载视频'.format(mid))
                    download_upload_recordings(start, end, zoom_download_url, mid, total_size, video,
                                                                 endpoint, object_key,
                                                                 group_name, obs_client)
                else:
                    key_size_map = {x['key']: x['size'] for x in objs['body']['contents']}
                    if object_key not in key_size_map.keys():
                        logger.info('meeting {}: OBS存储服务中无此对象，开始下载视频'.format(mid))
                        download_upload_recordings(start, end, zoom_download_url, mid, total_size, video,
                                                                     endpoint, object_key,
                                                                     group_name, obs_client)
                    elif object_key in key_size_map.keys() and key_size_map[object_key] >= total_size:
                        logger.info('meeting {}: OBS存储服务中已存在该对象且无需替换'.format(mid))
                    else:
                        logger.info('meeting {}: OBS存储服务中该对象需要替换，开始下载视频'.format(mid))
                        download_upload_recordings(start, end, zoom_download_url, mid, total_size, video,
                                                                     endpoint,
                                                                     object_key, group_name, obs_client)
            except Exception as e:
                logger.error(e)
