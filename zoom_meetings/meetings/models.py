from django.db import models

# Create your models here.
class LoginItem(models.Model):
    """登录表"""
    wechat_id = models.CharField('微信id', max_length=128, unique=True)
    login_type = models.CharField('登录类型', max_length=20)


class GroupItem(models.Model):
    """SIG组表"""
    group_name = models.CharField('组名', max_length=128, unique=True)
    # maintainer = models.CharField('维护者', max_length=20)  # 一个组可能有多个maintainer
    description = models.CharField('组描述', max_length=255)
    host_wechat_id = models.CharField('主持人微信id', max_length=128, null=True, blank=True)
    host_email = models.CharField('组主持人邮箱', max_length=128, null=True, blank=True)
    host_logo = models.CharField('主持人头像logo',max_length=128, null=True, blank=True)  # image
    # repositories = models.CharField('代码仓', max_length=128)  # 一个组下面对应有多个仓
    etherpad = models.TextField('etherpad', null=True, blank=True)


class MeetingItem(models.Model):
    """会议表"""
    meeting_type = {
        (1, '紧急会议'),
        (2, '预定会议')
    }
    meeting_id = models.CharField('会议id', max_length=20, null=True, blank=True)
    topic = models.CharField('会议主题', max_length=128)
    type = models.SmallIntegerField('会议类型', choices=meeting_type, default=2, null=True)
    start_time = models.CharField('会议开始时间', max_length=30)
    timezone = models.CharField('时区', max_length=50)
    duration = models.IntegerField('持续时间')
    group_id = models.CharField(max_length=128, null=True, blank=True)
    password = models.CharField('会议密码', max_length=128, null=True, blank=True)
    agenda = models.TextField('议程', null=True, blank=True)
    etherpad = models.TextField('etherpad', null=True, blank=True)
    zoom_host = models.EmailField('主持人邮箱', null=True, blank=True)
    # emails = models.EmailField('邮件')
    start_url = models.TextField('开启会议url', null=True, blank=True)
    join_url = models.CharField('进入会议url', max_length=128, null=True, blank=True)


class Community(models.Model):
    """社区表"""
    maintainer = models.CharField('维护者', max_length=128),
    group = models.ForeignKey(GroupItem, verbose_name = 'SIG组', on_delete=models.SET_NULL, null=True)


class Repository(models.Model):
    """仓库表"""
    repo = models.CharField('仓库', max_length=128),
    group = models.ForeignKey(GroupItem, verbose_name = 'SIG组', on_delete=models.SET_NULL, null=True)


class Email_list(models.Model):
    """邮件列表"""
    email = models.EmailField('受邀参会成员邮件')
    meeting_id = models.ForeignKey(MeetingItem, verbose_name = '会议号', on_delete=models.SET_NULL, null=True)