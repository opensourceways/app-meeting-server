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
