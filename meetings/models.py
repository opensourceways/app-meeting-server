from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    """用户表"""
    nickname = models.CharField(verbose_name='昵称', max_length=40, null=True, blank=True)
    gitee_name = models.CharField(verbose_name='gitee名称', max_length=40, null=True, blank=True)
    avatar = models.CharField(verbose_name='用户头像', max_length=255, null=True, blank=True)
    gender = models.SmallIntegerField(verbose_name='性别',choices=((0, '未知'), (1, '男'), (2, '女')),
                              default=0)
    openid = models.CharField(verbose_name='openid', max_length=32, unique=True, null=True, blank=True)
    password = models.CharField('密码', max_length=128, null=True, blank=True)
    unionid = models.CharField(verbose_name='unionid', max_length=128, unique=True, null=True, blank=True)
    status = models.SmallIntegerField(verbose_name='状态', choices=((0, '未登陆'), (1, '登陆')), default=0)
    level = models.SmallIntegerField(verbose_name='权限级别', choices=((1, '普通用户'), (2, '授权用户'), (3, '管理员')),
                                     default=1)
    signature = models.CharField(verbose_name='个性签名', max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, blank=True)
    last_login = models.DateTimeField(verbose_name='上次登录时间', auto_now=True, null=True, blank=True)

    USERNAME_FIELD = 'openid'


class Group(models.Model):
    """SIG组表"""
    group_name = models.CharField(verbose_name='组名', max_length=128, unique=True)
    home_page = models.CharField(verbose_name='首页', max_length=128, null=True, blank=True)
    maillist = models.EmailField(verbose_name='邮件列表', null=True, blank=True)
    irc = models.CharField(verbose_name='IRC频道', max_length=30, null=True, blank=True)
    etherpad = models.CharField(verbose_name='etherpad', max_length=255, null=True, blank=True)
    owners = models.TextField(verbose_name='maintainer列表', null=True, blank=True)
    app_home_page = models.CharField(verbose_name='app首页', max_length=128, null=True, blank=True)
    description = models.CharField(verbose_name='组描述', max_length=255, null=True, blank=True)


class GroupUser(models.Model):
    """组与用户表"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'user')


class Meeting(models.Model):
    """会议表"""
    topic = models.CharField(verbose_name='会议主题', max_length=128)
    group_name = models.CharField(verbose_name='SIG组', max_length=40, default='')
    sponsor = models.CharField(verbose_name='发起人', max_length=20)
    date = models.CharField(verbose_name='会议日期', max_length=30)
    start = models.CharField(verbose_name='会议开始时间', max_length=30)
    end = models.CharField(verbose_name='会议结束时间', max_length=30)
    duration = models.IntegerField(verbose_name='会议时长', null=True, blank=True)
    agenda = models.TextField(verbose_name='议程', default='', null=True, blank=True)
    etherpad = models.CharField(verbose_name='etherpad', max_length=255, null=True, blank=True)
    emaillist = models.TextField(verbose_name='邮件列表', null=True, blank=True)
    host_id = models.EmailField(verbose_name='host_id', null=True, blank=True)
    mid = models.CharField(verbose_name='会议id', max_length=20)
    timezone = models.CharField(verbose_name='时区', max_length=50, null=True, blank=True)
    password = models.CharField(verbose_name='密码', max_length=128, null=True, blank=True)
    start_url = models.TextField(verbose_name='开启会议url', null=True, blank=True)
    join_url = models.CharField(verbose_name='进入会议url', max_length=128, null=True, blank=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True, null=True, blank=True)
    is_delete = models.SmallIntegerField(verbose_name='是否删除', choices=((0, '否'), (1, '是')), default=0)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
