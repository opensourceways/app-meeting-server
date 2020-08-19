from django.contrib import admin

# Register your models here.
from meetings.models import LoginItem, GroupItem, MeetingItem, Community, Repository, Email_list


@admin.register(LoginItem)
class LoginAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'wechat_id', 'login_type')
    list_display_links = ('id', 'wechat_id', 'login_type')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('login_type',)  # 过滤器
    search_fields = ('id', 'login_type')  # 搜索字段


@admin.register(GroupItem)
class GroupAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'group_name', 'host_wechat_id', 'host_email', 'description')
    list_display_links = ('id', 'group_name', 'description')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('group_name',)  # 过滤器
    search_fields = ('id', 'group_name')  # 搜索字段


@admin.register(MeetingItem)
class MeetingAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'group_id', 'topic', 'start_time', 'duration', 'topic', 'meeting_id')
    list_display_links = ('id', 'group_id', 'topic', 'meeting_id')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('group_id', 'meeting_id', 'duration')  # 过滤器
    search_fields = ('id', 'group_id', 'duration')  # 搜索字段


# @admin.register(Community)
# class CommunityAdmin(admin.ModelAdmin):
#     list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
#     ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序
#
#     list_display = ('id', 'group', 'maintainer')
#     list_display_links = ('id', 'group', 'maintainer')     # 设置哪些字段可以点击进入编辑界面
#
#     list_filter = ('id', 'group', 'maintainer')  # 过滤器
#     search_fields = ('id', 'group', 'maintainer')  # 搜索字段


# @admin.register(Repository)
# class RepositoryAdmin(admin.ModelAdmin):
#     list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
#     ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序
#
#     list_display = ('id', 'group', 'repo')
#     list_display_links = ('id', 'group', 'repo')     # 设置哪些字段可以点击进入编辑界面
#
#     list_filter = ('id', 'group', 'repo')  # 过滤器
#     search_fields = ('id', 'group', 'repo')  # 搜索字段


@admin.register(Email_list)
class EmailLisrAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'email', 'meeting_id')
    list_display_links = ('id', 'email', 'meeting_id')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('id', 'email', 'meeting_id')  # 过滤器
    search_fields = ('id', 'email', 'meeting_id')  # 搜索字段