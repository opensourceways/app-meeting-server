from django.urls import path
from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView, UsersView, UserView, \
    GroupUserAddView, GroupUserView, MeetingDelView, MeetingsWeeklyView, MeetingsDailyView, MeetingsAllView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('groups/', GroupsView.as_view()),
    path('groups/<int:pk>/', GroupView.as_view()),
    path('meetings/', MeetingsView.as_view()),
    path('meetings/all/', MeetingsAllView.as_view()),
    path('meetings/weekly/', MeetingsWeeklyView.as_view()),
    path('meetings/daily/', MeetingsDailyView.as_view()),
    path('meetings/<int:mid>/', MeetingDelView.as_view()),
    path('meetings/<int:pk>', MeetingView.as_view()),
    path('users/', UsersView().as_view()),
    path('user/<int:pk>', UserView.as_view()),
    path('groupuser/new/', GroupUserAddView.as_view()),
    path('groupuser/', GroupUserView.as_view()),
]
