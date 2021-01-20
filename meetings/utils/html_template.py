def cover_content(topic, group_name, date, start_time, end_time):
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>cover</title>
    </head>
    <body style="text-align: center">
    <div style="display: inline-block; width: 63ream; height: 42rem">
        <img src="cover.png" alt="recording cover" style="margin-top: 5rem"/>
        <h1 style="color: #002FA7; margin-top: 3rem">{0}</h1>
        <h4>SIG: {1}</h4>
        <h4>Time: {2} {3}-{4}</h4>
    </div>
    </body>
    </html>
    """.format(topic, group_name, date, start_time, end_time)
    return content
