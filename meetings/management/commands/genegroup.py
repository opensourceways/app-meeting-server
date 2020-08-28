import requests
import lxml
import logging
from lxml.etree import HTML
from meetings.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    logger = logging.getLogger('log')

    def handle(self, *args, **options):
        url = 'https://gitee.com/openeuler/community/tree/master/sig'
        r = requests.get(url)
        html = HTML(r.content)
        assert isinstance(html, lxml.etree._Element)
        sigs_list = []
        i = 3
        while True:
            sig_name = html.xpath("//div[@id='tree-slider']/div[{}]/div[1]/a/@title".format(i))[0]
            sig_page = html.xpath("//div[@id='tree-slider']/div[{}]/div[1]/a/@href".format(i))[0]
            if sig_name == 'sigs.yaml':
                break
            # 获取所有sig的名称和页面地址
            sigs_list.append([sig_name, 'https://gitee.com' + sig_page])
            i += 2

        for sig in sigs_list:
            if sig[0] == 'sig-template':
                continue
            # 获取邮件列表
            r = requests.get(sig[1])
            html = HTML(r.text)
            assert isinstance(html, lxml.etree._Element)
            try:
                maillist = html.xpath('//li[contains(text(), "邮件列表")]/a/@href')[0].replace('mailto:', '')
            except IndexError:
                try:
                    maillist = html.xpath('//a[contains(text(), "邮件列表")]/@href')[0].rstrip('/').split('/')[-1]
                except IndexError:
                    maillist = 'dev@openeuler.org'
            if not maillist:
                    maillist = 'dev@openeuler.org'
            sig.append(maillist)

            # 获取IRC频道
            try:
                irc = html.xpath('//a[contains(text(), "IRC频道")]/@href')[0]
            except IndexError:
                try:
                    irc = html.xpath('//a[contains(text(), "IRC")]/@href')[0]
                except IndexError:
                    try:
                        irc = html.xpath('//*[contains(text(), "IRC")]/text()')[0].split(':')[1].strip().rstrip(')')
                    except IndexError:
                        irc = '#openeuler-dev'
            if '#' not in irc:
                irc = '#openeuler-dev'
            sig.append(irc)

            # 获取owners
            url = 'https://gitee.com/openeuler/community/blob/master/sig/{}/OWNERS'.format(sig[0])
            r = requests.get(url)
            html = HTML(r.text)
            assert isinstance(html, lxml.etree._Element)
            res = html.xpath('//div[@class="line"]/text()')
            owners = []
            for i in res[1:]:
                maintainer = i.strip().split('-')[-1].strip()
                owners.append(maintainer)
            owners = ','.join(owners)
            sig.append(owners)

            # 查询数据库，如果sig_name不存在，则创建sig信息；如果sig_name存在,则更新sig信息
            if not Group.objects.filter(group_name=sig[0]):
                Group.objects.create(group_name=sig[0], home_page=sig_page, owners=owners, maillist=maillist, irc=irc)
                self.logger.info("Create sig: {}".format(sig[0]))
                self.logger.info(sig)
            else:
                Group.objects.update(home_page=sig_page, owners=owners, maillist=maillist, irc=irc)
                self.logger.info("Update sig: {}".format(sig[0]))
                self.logger.info(sig)
