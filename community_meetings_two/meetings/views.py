import datetime
import json
import random
import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework_simplejwt import authentication

from meetings.models import User, Group, Meeting, GroupUser
from meetings.permissions import MaintainerPermission
from meetings.serializers import LoginSerializer, GroupSerializer, MeetingSerializer, UsersSerializer, \
    UserSerializer, AddGroupUserSerializer, GroupUserSerializer


class LoginView(GenericAPIView, CreateModelMixin, ListModelMixin):
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class GroupsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    @swagger_auto_schema(operation_summary='查询所有SIG组')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MeetingsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    # 未来一周的会议  /meetings/7days
    # queryset = Meeting.objects.filter(Q(is_delete=0) & (Q(date__gte=str(datetime.datetime.now())[:10]) & Q(date__lte=str(datetime.datetime.now() + datetime.timedelta(days=7))[:10])))
    # 今日的会议  /meetings/today
    # queryset = Meeting.objects.all().filter(Q(is_delete=0) & Q(date__exact=str(datetime.datetime.now())[:10]))
    authentication_classes = (TokenAuthentication)
    permission_classes = (permissions.IsAuthenticated, MaintainerPermission)

    @swagger_auto_schema(operation_summary='查询所有会议')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='创建会议')
    def post(self, request, *args, **kwargs):

        host_dict = settings.MEETING_HOSTS
        host_list = list(host_dict.values())
        random.shuffle(host_list)
        for host in list(host_list):
            # 调用zoom-api查询所有会议
            headers = {
                "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
            }
            res = requests.get("https://api.zoom.us/v2/users/{}/meetings".format(host), headers=headers)
            # 将查询出的所有会议的id放入一个list
            # if res:
            meetings_id_list = []
            for meeting in res.json()['meetings']:
                meetings_id_list.append(meeting['id'])

            # 遍历meetings_id_list，用meeting_id查询单个会议具体信息，若该会议处于开启状态，则查出该会议对应的host，并从随机hosts中排除掉
            for meeting_id in meetings_id_list:
                url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
                headers = {
                    "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

                response = requests.request("GET", url, headers=headers)
                if response.json()['status'] == 'started':
                    del host_dict[response.json()['host_id']]
                    break

        if len(host_dict) == 0:
            return JsonResponse({'code': 1000, 'massage': '暂无可用host,请稍后再试'})
        # 随机取一个可用的host
        host_email = random.choice(list(host_dict.values()))
        # 发送post请求，创建会议
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        data = self.request.data
        date = data['date']
        start = data['start_time']
        end = data['end_time']
        # user_id = User.objects.filter(id=data['user_id']).first().id
        # group_id = Group.objects.filter(group_name=data['group_name']).first().id
        if start >= end:
            return JsonResponse({'code': 1001, 'massage': '请输入正确的结束时间'})
        url = "https://api.zoom.us/v2/users/{}/meetings".format(host_email)
        response = requests.post(url, data=json.dumps(data), headers=headers)
        # 数据库生成数据
        Meeting.objects.create(
            meeting_id=response.json()['id'],
            topic=response.json()['topic'],
            date=date,
            start_time=start,
            end_time=end,
            timezone=response.json()['timezone'],
            password=response.json()['password'] if 'password' in data else '',
            agenda=data['agenda'] if 'agenda' in data else '',
            host_id=response.json()['host_id'],
            join_url=response.json()['join_url'],
            start_url=response.json()['start_url'],
            # user_id=user_id,
            # group_id=group_id
        )
        # 返回请求数据
        return JsonResponse(response.json())


class MeetingView(GenericAPIView, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()

    # 因本接口含所有会议信息，故不查询数据库
    def get(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

        response = requests.request("GET", url, headers=headers)
        return JsonResponse(response.json())
        # return self.retrieve(request, *args, **kwargs)

    # 数据库与zoom-api删除同步，作逻辑删除
    @swagger_auto_schema(operation_summary='删除一条会议')
    def delete(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}
        response = requests.request("DELETE", url, headers=headers)
        if response.status_code == 204:
            Meeting.objects.filter(meeting_id=meeting_id).update(is_delete=1)
            return JsonResponse({"code": 204, "massege": "Delete successfully."})
        else:
            return JsonResponse(response.json())


class UsersView(GenericAPIView, ListModelMixin):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
    # queryset = User.objects.all().order_by('nickname')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserView(GenericAPIView, UpdateModelMixin):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class GroupUserView(GenericAPIView, ListModelMixin):
    serializer_class = GroupUserSerializer
    queryset = GroupUser.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AddGroupUserView(GenericAPIView, CreateModelMixin):
    serializer_class = AddGroupUserSerializer
    queryset = GroupUser.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)






