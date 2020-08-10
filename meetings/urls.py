from django.urls import path
from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView, UsersView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('groups/', GroupsView.as_view()),
    path('groups/<int:pk>/', GroupView.as_view()),
    path('meetings/', MeetingsView.as_view()),
    path('meetings/<int:meeting_id>/', MeetingView.as_view()),
    path('users/', UsersView.as_view())
]