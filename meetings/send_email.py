import logging
import os
import smtplib
from django.conf import settings
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


logger = logging.getLogger('log')

def sendmail(topic, date, start, join_url, sig_name, toaddrs, enclosure_paths=None):
    start_time = ' '.join([date, start])
    toaddrs = toaddrs.replace(' ', '').replace('，', ',').replace(';', ',').replace('；', ',')
    toaddrs_list = toaddrs.split(',')
    # 构造邮件
    msg = MIMEMultipart()

    # 添加邮件主体
    body_of_email = '''
    <html>
    <body>
    <div class='zh'>
    <p>您好！</p>
    <p>openEuler {0} SIG 邀请您参加 {1} 召开的ZOOM会议</p>
    <p>会议主题：{3}</p>
    <p>会议链接：<a href="{2}">{2}</a></p>
    <p>更多资讯尽在：<a href="https://openeuler.org/zh/">https://openeuler.org/zh/</a></p>
    <br/>
    <br/>
    </div>
    <div class='en'>
    <p>Hello!</p>
    <p>openEuler {0} SIG invites you to attend the ZOOM conference will be held at {1},</p>
    <p>The subject of the conference is {3},</p>
    <p>You can join the meeting at <a href="{2}">{2}</a>.</p>
    <p><a href="https://openeuler.org/zh/">More information</a></p>
    </div>
    </body>
    </html>
    '''.format(sig_name, start_time, join_url, topic)
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
    msg['To'] = toaddrs

    # 登录服务器发送邮件
    try:
        gmail_username = settings.GMAIL_USERNAME
        gmail_password = settings.GMAIL_PASSWORD
        server = smtplib.SMTP(settings.SMTP_SERVER_HOST, settings.SMTP_SERVER_PORT)
        server.ehlo()
        server.starttls()
        server.login(gmail_username, gmail_password)
        server.sendmail(gmail_username, toaddrs_list, msg.as_string())
        logger.info('email sent: {}'.format(toaddrs))
        server.quit()
    except smtplib.SMTPException as e:
        logger.error(e)
