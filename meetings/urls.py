from django.urls import path
from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView, UsersExcludeView, UserView, \
    GroupUserAddView, MeetingDelView, MeetingsWeeklyView, MeetingsDailyView, \
    UsersIncludeView, UserGroupView, GroupUserDelView, UserInfoView, SigsView, MeetingsDataView, SigMeetingsDataView, \
    MyMeetingsView, AllMeetingsView, CollectView, CollectDelView, MyCollectionsView

urlpatterns = [
    path('login/', LoginView.as_view()),  # 登陆
    path('groups/', GroupsView.as_view()),  # 查询所有SIG组的名称
    path('sigs/', SigsView.as_view()),  # 查询所有SIG组的名称、首页、邮件列表、IRC频道及成员的nickname、gitee_name、avatar
    path('groups/<int:pk>/', GroupView.as_view()),  # 查询单个SIG组详情
    path('meetings/', MeetingsView.as_view()),  # 新建会议
    path('meetings_weekly/', MeetingsWeeklyView.as_view()),  # 查询前后一周会议详情
    path('meetings_daily/', MeetingsDailyView.as_view()),   # 查询当日会议详情
    path('meeting/<int:mid>/', MeetingDelView.as_view()),  # 删除会议
    path('meetings/<int:pk>/', MeetingView.as_view()),  # 查询单个会议详情
    path('users_exclude/<int:pk>/', UsersExcludeView.as_view()),  # 查询不在该组的所有成员的nickname、gitee_name、avatar
    path('users_include/<int:pk>/', UsersIncludeView.as_view()),  # 获取该SIG组的所有成员的nickname、gitee_name、avatar
    path('user/<int:pk>/', UserView.as_view()),  # 更新gitee_name
    path('usergroup/<int:pk>/', UserGroupView.as_view()),  # 查询该成员的组名以及etherpad
    path('groupuser/action/new/', GroupUserAddView.as_view()),  # 批量给SIG组新增成员
    path('groupuser/action/del/', GroupUserDelView.as_view()),  # 批量删除SIG组成员
    path('userinfo/<int:pk>/', UserInfoView.as_view()),  # 查询本机用户的level和gitee_name
    path('meetingsdata/', MeetingsDataView.as_view()),  # 网页会议数据
    path('sigmeetingsdata/<int:pk>/', SigMeetingsDataView.as_view()),  # 网页SIG会议数据
    path('mymeetings/', MyMeetingsView.as_view()),  # 查询我创建的会议
    path('allmeetings/', AllMeetingsView.as_view()),  # 查询所有会议
    path('collect/', CollectView.as_view()),  # 添加收藏
    path('collect/<int:pk>/', CollectDelView.as_view()),  # 取消收藏
    path('collections/', MyCollectionsView.as_view())  # 我收藏的会议 
]
