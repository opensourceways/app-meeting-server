# Create your views here.
import json
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from meetings.models import LoginItem, GroupItem, MeetingItem
from meetings.serializers import LoginSerializer, GroupSerializer, GroupsSerializer, MeetingSerializer, \
    MeetingsSerializer
import requests
from django.http import JsonResponse
from community_meetings_two.settings import zoom_token


token = zoom_token
class LoginView(GenericAPIView, CreateModelMixin):
    serializer_class = LoginSerializer
    queryset = LoginItem.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = GroupSerializer
    queryset = GroupItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = GroupsSerializer
    queryset = GroupItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MeetingsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = MeetingSerializer
    queryset = MeetingItem.objects.all()

    def get(self, request, *args, **kwargs):
        headers = {
            "authorization": "Bearer {}".format(token)
        }
        response = requests.get("https://api.zoom.us/v2/users/genedna@hey.com/meetings", headers=headers)
        return JsonResponse(response.json())

    def post(self, request, *args, **kwargs):
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(token)
        }
        data = self.request.data
        url = "https://api.zoom.us/v2/users/genedna@hey.com/meetings"
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return JsonResponse({"data": response.json()})


class MeetingView(GenericAPIView, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = MeetingsSerializer
    queryset = MeetingItem.objects.all

    def get(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(token)}

        response = requests.request("GET", url, headers=headers)
        return JsonResponse({"data": response.json()})

    def delete(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(token)}
        response = requests.request("DELETE", url, headers=headers)
        if response.status_code == 204:
            return JsonResponse({"code": 204, "massege": "Delete successfully."})
        else:
            return JsonResponse(response.json())