# import os
# import django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "community_meetings.settings")
# django.setup()
import requests
import lxml
import logging
from lxml.etree import HTML
from meetings.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    logger = logging.getLogger()

    def handle(self, *args, **options):
        url = 'https://gitee.com/openeuler/community/tree/master/sig'
        r = requests.get(url)
        html = HTML(r.content)
        assert isinstance(html, lxml.etree._Element)
        sigs_list = []
        i = 3
        while True:
            sig_name, sig_page = html.xpath("//div[@id='tree-slider']/div[{}]/div[1]/a/@title".format(i))[0], html.xpath("//div[@id='tree-slider']/div[{}]/div[1]/a/@href".format(i))[0]
            if sig_name == 'sigs.yaml':
                break
            # 获取所有sig的名称和页面地址
            sigs_list.append((sig_name, 'https://gitee.com' + sig_page))
            i += 2

        for sig in sigs_list:
            sig_name = sig[0]
            sig_page = sig[1]

            if not Group.objects.filter(group_name=sig_name):
                print(sig)
                Group.objects.create(group_name=sig_name, home_page=sig_page)
            else:
                Group.objects.update(home_page=sig_page)