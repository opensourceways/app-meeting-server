# app-meeting-server
The repository is a django project for community meetings.


#### prepare
1. python: 3.5+
2. django:3.0.8
3. mysql:8.0.18  
#### install
database is required to run this application, we utilize docker to setting up our developing environment, use command
below to quick run server on localhost:
```
# seeting up environment
make dev-env
# running on virtualenv
source meetingserverenv/bin/activate
python3 manage.py runserver
```

#### create a project with Pycharm
File ==> New Project ==> Django:
You can create a new interpreter or use the `Existing interpreter`.Then give your app a `Application name` in `More settings`, you can also run `python manage.py startapp appname` to build your app.
After creating, run `python manage.py runserver`.The following output means that you've started the django project. 
```text
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).

You have 17 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s):admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.

August 06, 2020 - 15:32:56
Django version 2.2.5, using settings 'untitled.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.

```

#### notice
- Check your mysql username and password.If you can't link to mysql(it return a code 1045 mostly),maybe you need to add the following in `meetings/__init__.py`.
```text
import pymysql
pymysql.install_as_MySQLdb()
```
- Most APIs may need a token.After all configured you can run `python manage.py runserver 8000 thetoken` to introduce the token.
 
