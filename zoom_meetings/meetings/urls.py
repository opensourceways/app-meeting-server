from django.urls import path

from meetings.views import LoginView, GroupView, GroupsView, MeetingView, MeetingsView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('groups/', GroupView.as_view()),
    path('groups/<int:pk>/', GroupsView.as_view()),
    path('meetings/', MeetingView.as_view()),
    path('meetings/<int:pk>/', MeetingsView.as_view())
]