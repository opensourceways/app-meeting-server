from django.urls import path
from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView, UsersExcludeView, UserView, \
    GroupUserAddView, MeetingDelView, MeetingsWeeklyView, MeetingsDailyView, \
    UsersIncludeView, UserGroupView, MeetingsInGroupView, GroupUserDelView

urlpatterns = [
    path('login/', LoginView.as_view()),  # 登陆
    path('groups/', GroupsView.as_view()),  # 查询所有SIG组
    path('groups/<int:pk>/', GroupView.as_view()),  # 查询单个SIG组
    path('meetings/', MeetingsView.as_view()),  # 新建会议
    path('meetings_weekly/', MeetingsWeeklyView.as_view()),  # 查询前后一周会议
    path('meetings_daily/', MeetingsDailyView.as_view()),   # 查询当日会议
    path('meeting/<int:mid>/', MeetingDelView.as_view()),  # 删除会议
    path('meetings/<int:pk>/', MeetingView.as_view()),  # 查询单个会议
    path('users_exclude/<int:pk>/', UsersExcludeView.as_view()),  # 查询不在该组的所有成员
    path('users_include/<int:pk>/', UsersIncludeView.as_view()),  # 查询在该组的所有成员
    path('user/<int:pk>/', UserView.as_view()),  # 更新gitee_name获取该SIG组的所有成员
    path('usergroup/<int:pk>/', UserGroupView.as_view()),  # 查询该成员的组名以及etherpad
    path('groupuser_new/', GroupUserAddView.as_view()),  # 批量给SIG组新增成员
    path('groupuser_del/', GroupUserDelView.as_view()),  # 批量删除SIG组成员
    path('userinfo/<int:pk>/', UserInfoView.as_view()), # 查询本机用户的level和gitee_name
]
