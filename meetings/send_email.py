import logging
import re
import smtplib
from django.conf import settings
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from meetings.utils.generate_email_template import *

logger = logging.getLogger('log')


def sendmail(topic, date, start, join_url, sig_name, toaddrs, summary=None, record=None, enclosure_paths=None):
    start_time = ' '.join([date, start])
    toaddrs = toaddrs.replace(' ', '').replace('，', ',').replace(';', ',').replace('；', ',')
    toaddrs_list = toaddrs.split(',')
    error_addrs = []
    for addr in toaddrs_list:
        if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', addr):
            error_addrs.append(addr)
            toaddrs_list.remove(addr)
    toaddrs_string = ','.join(toaddrs_list)
    # 发送列表默认添加community和dev的邮件列表
    toaddrs_list.extend(['community@openeuler.org', 'dev@openeuler.org'])
    # 发送列表去重，排序
    toaddrs_list = sorted(list(set(toaddrs_list)))

    # 构造邮件
    msg = MIMEMultipart()

    # 添加邮件主体
    body_of_email = None
    if not summary and not record:
        body_of_email = email_template(sig_name, start_time, join_url, topic)
    if summary and not record:
        body_of_email = email_template_with_agenda(sig_name, start_time, join_url, topic, summary)
    if not summary and record:
        body_of_email = record_email_template(sig_name, start_time, join_url, topic)
    if summary and record:
        body_of_email = record_email_template_with_agenda(sig_name, start_time, join_url, topic, summary)

    content = MIMEText(body_of_email, 'html', 'utf-8')
    msg.attach(content)

    # 添加邮件附件
    paths = enclosure_paths
    if paths:
        for file_path in paths:
            file = MIMEApplication(open(file_path, 'rb').read())
            file.add_header('Content-Disposition', 'attachment', filename=file_path)
            msg.attach(file)

    # 完善邮件信息
    msg['Subject'] = topic
    msg['From'] = 'openEuler conference'
    msg['To'] = toaddrs_string

    # 登录服务器发送邮件
    try:
        gmail_username = settings.GMAIL_USERNAME
        gmail_password = settings.GMAIL_PASSWORD
        server = smtplib.SMTP(settings.SMTP_SERVER_HOST, settings.SMTP_SERVER_PORT)
        server.ehlo()
        server.starttls()
        server.login(gmail_username, gmail_password)
        server.sendmail(gmail_username, toaddrs_list, msg.as_string())
        logger.info('email string: {}'.format(toaddrs))
        logger.info('error addrs: {}'.format(error_addrs))
        logger.info('email sent: {}'.format(toaddrs_string))
        server.quit()
    except smtplib.SMTPException as e:
        logger.error(e)
