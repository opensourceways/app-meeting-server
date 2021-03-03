import logging
import os
import sys
from bilibili_api.user import get_videos_g
from django.core.management.base import BaseCommand
from meetings.models import Record
from obs import ObsClient

logger = logging.getLogger('log')


class Command(BaseCommand):
    def handle(self, *args, **options):
        uid = int(os.getenv('BILI_UID', ''))
        if not uid:
            logger.error('uid is required')
            sys.exit(1)
        videos = get_videos_g(uid=uid)
        # 所有过审视频的bvid集合
        bvs = [x['bvid'] for x in videos]
        logger.info('所有B站过审视频的bvid: {}'.format(bvs))
        logger.info('B站过审视频数: {}'.format(len(bvs)))
        access_key_id = os.getenv('ACCESS_KEY_ID', '')
        secret_access_key = os.getenv('SECRET_ACCESS_KEY', '')
        endpoint = os.getenv('OBS_ENDPOINT', '')
        bucketName = os.getenv('OBS_BUCKETNAME', '')
        if not access_key_id or not secret_access_key or not endpoint or not bucketName:
            logger.error('losing required arguments for ObsClient')
            sys.exit(1)
        obs_client = ObsClient(access_key_id=access_key_id,
                               secret_access_key=secret_access_key,
                               server='https://{}'.format(endpoint))
        bili_mids = [int(x.mid) for x in Record.objects.filter(platform='bilibili', url__isnull=True)]
        logger.info('所有上传B站的会议的mid: {}'.format(bili_mids))
        for mid in bili_mids:
            obs_record = Record.objects.get(mid=mid, platform='obs')
            url = obs_record.url
            object_key = url.split('/', 3)[-1]
            # 获取对象的metadata
            metadata = obs_client.getObjectMetadata(bucketName, object_key)
            metadata_dict = {x: y for x, y in metadata['header']}
            if not metadata_dict['bvid']:
                logger.info('meeting {}: 未上传B站，跳过'.format(mid))
            else:
                logger.info('meeting {}: bvid为{}'.format(mid, metadata_dict['bvid']))
                if metadata_dict['bvid'] not in bvs:
                    logger.info('meetings: {}: 上传至B站，还未过审'.format(mid))
                else:
                    bili_url = 'https://www.bilibili.com/{}'.format(metadata_dict['bvid'])
                    Record.objects.filter(mid=mid, platform='bilibili').update(url=bili_url)
                    logger.info('meeting {}: B站已过审，更新数据库'.format(mid))
