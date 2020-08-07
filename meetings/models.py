from django.db import models
# Create your models here.


class LoginItem(models.Model):
    """登录表"""
    wechat_id = models.CharField('微信id', max_length=128, unique=True)
    login_type = models.CharField('登录类型', max_length=20)


class GroupItem(models.Model):
    """SIG组表"""
    group_name = models.CharField('组名', max_length=128, unique=True)
    description = models.CharField('组描述', max_length=255)
    host_wechat_id = models.CharField('主持人微信id', max_length=128, null=True, blank=True)
    host_email = models.CharField('组主持人邮箱', max_length=128, null=True, blank=True)
    host_logo = models.CharField('主持人头像logo', max_length=128, null=True, blank=True)
    etherpad = models.TextField('etherpad', null=True, blank=True)


class MeetingItem(models.Model):
    """会议表"""
    meeting_type = {
        (1, '紧急会议'),
        (2, '预定会议')
    }
    meeting_id = models.CharField('会议id', max_length=20, null=True, blank=True)
    topic = models.CharField('会议主题', max_length=128, default=2, null=True)
    type = models.SmallIntegerField('会议类型', choices=meeting_type, default=2, null=True)
    start_time = models.CharField('会议开始时间', max_length=30, default=2, null=True)
    timezone = models.CharField('时区', max_length=50, default=2, null=True)
    duration = models.IntegerField('持续时间', default=2, null=True)
    group_id = models.CharField(max_length=128, null=True, blank=True)
    password = models.CharField('会议密码', max_length=128, null=True, blank=True)
    agenda = models.TextField('议程', null=True, blank=True)
    etherpad = models.TextField('etherpad', null=True, blank=True)
    zoom_host = models.EmailField('主持人邮箱', null=True, blank=True)
    # emails = models.EmailField('邮件')
    start_url = models.TextField('开启会议url', null=True, blank=True)
    join_url = models.CharField('进入会议url', max_length=128, null=True, blank=True)


class Maintainers(models.Model):
    """维护者"""
    maintainer = models.CharField('维护者', max_length=128),
    wechat_union_id = models.CharField('wechat_union_id', max_length=128),
    maintainer_name = models.CharField('自定义名称', max_length=128),
    maintainer_logo = models.CharField('头像', max_length=255),
    maintainer_email = models.EmailField('邮件'),
    maintainer_description = models.TextField('描述'),
    group = models.ForeignKey(GroupItem, verbose_name='SIG组', on_delete=models.SET_NULL, null=True)


class Repository(models.Model):
    """仓库表"""
    repo = models.CharField('仓库', max_length=128),
    group = models.ForeignKey(GroupItem, verbose_name='SIG组', on_delete=models.SET_NULL, null=True)


class Email_list(models.Model):
    """邮件列表"""
    email = models.EmailField('受邀参会成员邮件')
    meeting_id = models.ForeignKey(MeetingItem, verbose_name='会议号', on_delete=models.SET_NULL, null=True)