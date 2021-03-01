def cover_content(topic, group_name, date, start_time, end_time):
    content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>cover</title>
    </head>
    <body>
        <div style="display: inline-block; height: 688px; width: 1024px; text-align: center; background-image: url('cover.png')">
            <p style="font-size: 100px;margin-top: 150px; color: white"><b>{0}</b></p>
            <p style="font-size: 80px; margin: 0; color: white">SIG: {1}</p>
            <p style="font-size: 60px; margin: 0; color: white">Time: {2} {3}-{4}</p>
        </div>
    </body>
    </html>
    """.format(topic, group_name, date, start_time, end_time)
    return content
