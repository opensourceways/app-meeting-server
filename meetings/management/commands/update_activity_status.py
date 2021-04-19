import datetime
import logging
from meetings.models import Activity
from django.core.management import BaseCommand

logger = logging.getLogger('log')


def update_activity_status():
    logger.info('start to update activity status')
    activities = Activity.objects.filter(is_delete=0, status__in=[3, 4, 5])
    today = datetime.date.today().strftime('%Y-%m-%d')
    for activity in activities:
        if activity.date == today and activity.status == 3:
            Activity.objects.filter(id=activity.id).update(status=4)
            logger.info(
                '\nid: {0}\ndate: {1}\ntitle: {2}\nenterprise: {3}\nsponsor: {4}'.format(activity.id,
                                                                                         activity.date,
                                                                                         activity.title,
                                                                                         activity.user.enterprise,
                                                                                         activity.user.gitee_name))
            logger.info('update activity status from publishing to going.')
        if activity.date < today and activity.status == 4:
            Activity.objects.filter(id=activity.id).update(status=5)
            logger.info(
                '\nid: {0}\ndate: {1}\ntitle: {2}\nenterprise: {3}\nsponsor: {4}'.format(activity.id,
                                                                                         activity.date,
                                                                                         activity.title,
                                                                                         activity.user.enterprise,
                                                                                         activity.user.gitee_name))
            logger.info('update activity status from going to completed.')
    logger.info('All done. Waiting for next task...')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            update_activity_status()
        except Exception as e:
            logger.error(e)
