from django.db import models


class User(models.Model):
    """用户表"""
    nickname = models.CharField(verbose_name='昵称', max_length=128, null=True, blank=True)
    gitee_name = models.CharField(verbose_name='gitee名称', max_length=128, null=True, blank=True)
    avatar = models.CharField(verbose_name='用户头像', max_length=128, null=True, blank=True)
    gender = models.CharField(verbose_name='性别', max_length=6, choices=((0, '女'), (1, '男')), null=True, blank=True)
    openid = models.CharField(verbose_name='openid', max_length=128, unique=True, null=True, blank=True)
    unionid = models.CharField(verbose_name='unionid', max_length=128, unique=True, null=True, blank=True)
    status = models.SmallIntegerField(verbose_name='状态', choices=((0, '未登陆'), (1, '登陆')), default=0)
    level = models.SmallIntegerField(verbose_name='权限级别', choices=((1, '普通用户'), (2, '授权用户'), (3, '管理员')),
                                     default=1)
    signature = models.CharField(verbose_name='个性签名', max_length=255, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_login_time = models.DateTimeField(verbose_name='最近登陆时间', auto_now=True)


class Group(models.Model):
    """SIG组表"""
    group_name = models.CharField(verbose_name='组名', max_length=128, unique=True)
    description = models.CharField(verbose_name='组描述', max_length=255, null=True, blank=True)
    etherpad = models.TextField(verbose_name='etherpad', null=True, blank=True)
    read_me = models.CharField(verbose_name='SIG文档', max_length=128, null=True, blank=True)
    user = models.ManyToManyField(User, verbose_name='用户')


class Meeting(models.Model):
    """会议表"""
    meeting_id = models.CharField(verbose_name='会议id', max_length=20, unique=True, null=True, blank=True)
    topic = models.CharField(verbose_name='会议主题', max_length=128, default='Zoom Meeting')
    start_time = models.CharField(verbose_name='会议开始时间', max_length=30)
    end_time = models.CharField(verbose_name='会议结束时间', max_length=30)
    timezone = models.CharField(verbose_name='时区', max_length=50, default='Asia/Shanghai')
    password = models.CharField(verbose_name='会议密码', max_length=128, null=True, blank=True)
    agenda = models.TextField(verbose_name='议程', default='', null=True, blank=True)
    etherpad = models.CharField(verbose_name='etherpad',max_length=255, null=True, blank=True)
    host_id = models.EmailField(verbose_name='host_id', null=True, blank=True)
    start_url = models.TextField(verbose_name='开启会议url', null=True, blank=True)
    join_url = models.CharField(verbose_name='进入会议url', max_length=128, null=True, blank=True)
    is_delete = models.SmallIntegerField(verbose_name='是否删除', choices=((0, '否'), (1, '是')), default=0)
    group = models.ForeignKey(Group, verbose_name='SIG组', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.SET_NULL, null=True)



