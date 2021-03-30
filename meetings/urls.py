from django.urls import path
from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView, UsersExcludeView, UserView, \
    GroupUserAddView, MeetingDelView, MeetingsWeeklyView, MeetingsDailyView, UsersIncludeView, UserGroupView, \
    GroupUserDelView, UserInfoView, SigsView, MeetingsDataView, SigMeetingsDataView, MyMeetingsView, AllMeetingsView, \
    CollectView, CollectDelView, MyCollectionsView, ParticipantsView, SponsorsView, NonSponsorView, SponsorAddView, \
    SponsorDelView, SponsorInfoView, DraftsView, DraftView, ActivityPublishView, ActivityRejectView, ActivityDelView, \
    ActivityView, ActivitiesView, RecentActivitiesView, SponsorActivitiesView, ActivityRetrieveView, \
    ActivityUpdateView, ActivityDraftView, ActivitiesDraftView, SponsorActivityDraftView, DraftUpdateView, \
    DraftPublishView, SponsorActivitiesPublishingView, ActivityCollectView, ActivityCollectDelView, \
    MyActivityCollectionsView, ActivityRegisterView, ApplicantInfoView, RegisterActivitiesView, ApplicantsInfoView, \
    FeedbackView, CountActivitiesView, MyCountsView, TicketView

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
    path('collections/', MyCollectionsView.as_view()),  # 我收藏的会议 
    path('participants/<int:mid>/', ParticipantsView.as_view()),  # 查询会议的参会者
    path('sponsors/', SponsorsView.as_view()),  # 活动发起人列表
    path('nonsponsors/', NonSponsorView.as_view()),  # 非活动发起人列表
    path('sponsor/action/new/', SponsorAddView.as_view()),  # 批量添加活动发起人
    path('sponsor/action/del/', SponsorDelView.as_view()),  # 批量删除活动发起人
    path('sponsorinfo/<int:pk>/', SponsorInfoView.as_view()),  # 修改活动发起人信息
    path('drafts/', DraftsView.as_view()),  # 审核列表
    path('draft/<int:pk>/', DraftView.as_view()),  # 待发布详情
    path('activitypublish/<int:pk>/', ActivityPublishView.as_view()),  # 通过审核
    path('activityreject/<int:pk>/', ActivityRejectView.as_view()),  # 驳回申请
    path('activitydel/<int:pk>/', ActivityDelView.as_view()),  # 删除活动
    path('activity/', ActivityView.as_view()),  # 创建活动并申请发布
    path('activities/', ActivitiesView.as_view()),  # 活动列表
    path('recentactivities/', RecentActivitiesView.as_view()),  # 最近的活动
    path('sponsoractivities/', SponsorActivitiesView.as_view()),  # 活动发起人的活动列表
    path('activity/<int:pk>/', ActivityRetrieveView.as_view()),  # 查询单个活动
    path('activityupdate/<int:pk>/', ActivityUpdateView.as_view()),  # 修改活动
    path('activitydraft/', ActivityDraftView.as_view()),  # 创建活动草案
    path('activitiesdraft/', ActivitiesDraftView.as_view()),  # 活动发起人的活动草案列表
    path('sponsoractivitydraft/<int:pk>/', SponsorActivityDraftView.as_view()),  # 查询、删除活动草案
    path('draftupdate/<int:pk>/', DraftUpdateView.as_view()),  # 修改草案
    path('draftpublish/<int:pk>/', DraftPublishView.as_view()),  # 草案申请发布活动
    path('sponsoractivitiespublishing/',SponsorActivitiesPublishingView.as_view()),  # 发布中(个人)的活动
    path('collectactivity/', ActivityCollectView().as_view()),  # 收藏活动
    path('collectactivitydel/<int:pk>/', ActivityCollectDelView.as_view()),  # 取消收藏活动
    path('collectactivities/', MyActivityCollectionsView.as_view()),  # 我收藏的活动列表
    path('activityregister/', ActivityRegisterView.as_view()),  # 活动报名
    path('applicantinfo/<int:pk>/', ApplicantInfoView.as_view()),  # 报名者信息详情
    path('registeractivities/', RegisterActivitiesView.as_view()),  # 我报名的活动列表
    path('applicantsinfo/', ApplicantsInfoView.as_view()),  # 报名者信息列表
    path('feedback/', FeedbackView.as_view()),  # 意见反馈
    path('countactivities/', CountActivitiesView.as_view()),  # 各类活动计数
    path('mycounts/', MyCountsView.as_view()),  # 我的各类计数
    path('ticket/<int:pk>/', TicketView.as_view()),  # 查看活动门票
]
