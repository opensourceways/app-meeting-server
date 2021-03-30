def email_template(sig_name, start_time, join_url, topic):
    body = """
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
    """.format(sig_name, start_time, join_url, topic)
    return body


def email_template_with_agenda(sig_name, start_time, join_url, topic, summary):
    body = """
    <html>
    <body>
    <div class='zh'>
    <p>您好！</p>
    <p>openEuler {0} SIG 邀请您参加 {1} 召开的ZOOM会议</p>
    <p>会议主题：{3}</p>
    <pre style="font-family: 'Microsoft YaHei',serif">会议内容：{4}</pre>
    <p>会议链接：<a href="{2}">{2}</a></p>
    <p>更多资讯尽在：<a href="https://openeuler.org/zh/">https://openeuler.org/zh/</a></p>
    <br/>
    <br/>
    </div>
    <div class='en'>
    <p>Hello!</p>
    <p>openEuler {0} SIG invites you to attend the ZOOM conference will be held at {1},</p>
    <p>The subject of the conference is {3},</p>
    <pre style="font-family: 'Microsoft YaHei UI',serif">Summary: {4}</pre>
    <p>You can join the meeting at <a href="{2}">{2}</a>.</p>
    <p><a href="https://openeuler.org/zh/">More information</a></p>
    </div>
    </body>
    </html>
    """.format(sig_name, start_time, join_url, topic, summary)
    return body


def record_email_template(sig_name, start_time, join_url, topic):
    body = """
    <html>
    <body>
    <div class='zh'>
    <p>您好！</p>
    <p>openEuler {0} SIG 邀请您参加 {1} 召开的ZOOM会议(自动录制)</p>
    <p>会议主题：{3}</p>
    <p>会议链接：<a href="{2}">{2}</a></p>
    <p>更多资讯尽在：<a href="https://openeuler.org/zh/">https://openeuler.org/zh/</a></p>
    <br/>
    <br/>
    </div>
    <div class='en'>
    <p>Hello!</p>
    <p>openEuler {0} SIG invites you to attend the ZOOM conference(auto recording) will be held at {1},</p>
    <p>The subject of the conference is {3},</p>
    <p>You can join the meeting at <a href="{2}">{2}</a>.</p>
    <p><a href="https://openeuler.org/zh/">More information</a></p>
    </div>
    </body>
    </html>
    """.format(sig_name, start_time, join_url, topic)
    return body


def record_email_template_with_agenda(sig_name, start_time, join_url, topic, summary):
    body = """
    <html>
    <body>
    <div class='zh'>
    <p>您好！</p>
    <p>openEuler {0} SIG 邀请您参加 {1} 召开的ZOOM会议(自动录制)</p>
    <p>会议主题：{3}</p>
    <pre style="font-family: 'Microsoft YaHei',serif">会议内容：{4}</pre>
    <p>会议链接：<a href="{2}">{2}</a></p>
    <p>更多资讯尽在：<a href="https://openeuler.org/zh/">https://openeuler.org/zh/</a></p>
    <br/>
    <br/>
    </div>
    <div class='en'>
    <p>Hello!</p>
    <p>openEuler {0} SIG invites you to attend the ZOOM conference(auto recording) will be held at {1},</p>
    <p>The subject of the conference is {3},</p>
    <pre style="font-family: 'Microsoft YaHei UI',serif">Summary: {4}</pre>
    <p>You can join the meeting at <a href="{2}">{2}</a>.</p>
    <p><a href="https://openeuler.org/zh/">More information</a></p>
    </div>
    </body>
    </html>
    """.format(sig_name, start_time, join_url, topic, summary)
    return body


def feedback_email_template(feedback_type, feedback_email, feedback_content):
    body = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <p>反馈类型：{0}</p>
        <p>反馈者邮箱：{1}</p>
        <p>反馈内容：{2}</p>
    </body>
    </html>
    """.format(feedback_type, feedback_email, feedback_content)
    return body


def reply_email_template():
    body = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <p>您好!</p>
        <p>感谢您给 openEuler 小程序提供的宝贵建议，我们将尽快处理此问题。为您提供良好的社区体验是我们不懈追求的目标。</p>
        <p style="text-align: right">openEuler 团队</p>
        <br/>
        <p>Hello.</p>
        <p>Thank you for your suggestion on the openEuler applet. We will address this issue as soon as possible. It is our unremitting goal to provide you with a good community experience.</p>
        <p>openEuler Team</p>
    </body>
    </html>
    """
    return body


def applicants_info_template():
    body = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title></title>
    </head>
    <body>
        <p>详细内容请查看csv附件</p>
    </body>
    </html>
    """
    return body
