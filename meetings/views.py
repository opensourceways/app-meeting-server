import datetime
import json
import random
import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework_simplejwt import authentication
from meetings.models import User, Group, Meeting, GroupUser
from meetings.permissions import MaintainerPermission, AdminPermission
from meetings.serializers import LoginSerializer, GroupsSerializer, MeetingSerializer, UsersSerializer, \
    UserSerializer, GroupUserSerializer, GroupUserAddSerializer, GroupSerializer


class LoginView(GenericAPIView, CreateModelMixin, ListModelMixin):
    """小程序授权登陆"""
    serializer_class = LoginSerializer
    queryset = User.objects.all()
    @swagger_auto_schema(operation_summary='用户注册与授权登陆')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class GroupsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    """SIG组"""
    serializer_class = GroupsSerializer
    queryset = Group.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    # authentication_classes = (TokenAuthentication,)
    permission_classes = (AdminPermission,)

    @swagger_auto_schema(operation_summary='查询所有SIG组')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    @swagger_auto_schema(operation_summary='创建SIG组')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    """单个SIG操作"""
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AdminPermission,)

    @swagger_auto_schema(operation_summary='查询SIG组')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='修改SIG组')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='删除SIG组')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UsersView(GenericAPIView, ListModelMixin):
    """查询用户列表"""
    serializer_class = UsersSerializer
    queryset = User.objects.all().order_by('nickname')

    @swagger_auto_schema(operation_summary='按昵称排序查询用户列表')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class UserView(GenericAPIView, UpdateModelMixin):
    """更新用户gitee_name"""
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(operation_summary='更新用户gitee_name')
    def put(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        gitee_name = request.data['gitee_name']
        # 有gitee_name,若gitee_name重复则返回；不重复则更新用户信息并将level置为2;gitee_name不存在则将gitee_name置空，level改为1
        if gitee_name:
            if User.objects.get(gitee_name=gitee_name):
                return JsonResponse({'code':400, 'msg':'gitee_name重复'})
            User.objects.filter(id=id).update(gitee_name=gitee_name, level=2)
        else:
            User.objects.filter(id=id).update(gitee_name=gitee_name, level=1)
        return self.update(request, *args, **kwargs)


class GroupUserView(GenericAPIView, ListModelMixin):
    """查询SIG组与用户关系列表"""
    serializer_class = GroupUserSerializer
    queryset = GroupUser.objects.all()

    @swagger_auto_schema(operation_summary='查询SIG组与用户关系列表')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GroupUserAddView(GenericAPIView, CreateModelMixin):
    """SIG组新增用户"""
    serializer_class = GroupUserAddSerializer
    queryset = GroupUser.objects.all()

    @swagger_auto_schema(operation_summary='SIG组新增用户')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MeetingsAllView(GenericAPIView, ListModelMixin):
    """查询所有会议"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()

    @swagger_auto_schema(operation_summary='查询所有会议')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MeetingsWeeklyView(GenericAPIView, ListModelMixin):
    """查询未来一周的所有会议"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.filter(Q(is_delete=0) & (Q(date__gte=str(datetime.datetime.now())[:10]) & Q(date__lte=str(datetime.datetime.now() + datetime.timedelta(days=7))[:10])))

    @swagger_auto_schema(operation_summary='查询未来一周的所有会议')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MeetingsDailyView(GenericAPIView, ListModelMixin):
    """查询本日的所有会议"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all().filter(Q(is_delete=0) & Q(date__exact=str(datetime.datetime.now())[:10]))

    @swagger_auto_schema(operation_summary='查询本日的所有会议')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MeetingsView(GenericAPIView, CreateModelMixin):
    """创建会议"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    # authentication_classes = (TokenAuthentication,)

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
        try:
            data = self.request.data
            date = data['date']
            start = data['start']
            end = data['end']
            user_id = User.objects.filter(id=data['user_id']).first().id
            group_id = Group.objects.filter(group_name=data['group_name']).first().id
        except:
            return JsonResponse({'code': 1000, 'massage': '创建会议条件不足'})
        if start >= end:
            return JsonResponse({'code': 1001, 'massage': '请输入正确的结束时间'})
        # start_time = date + 'T' + start + 'Z'
        # duration = (int(end[:2])-int(start[:2]))* 60 + (int(end[3:5]) - int(start[3:5]))
        # new_data = {}
        # new_data['start_time'] = start_time
        # new_data['duration'] = duration
        url = "https://api.zoom.us/v2/users/{}/meetings".format(host_email)
        response = requests.post(url, data=json.dumps(data), headers=headers)
        # 数据库生成数据
        Meeting.objects.create(
            meeting_id=response.json()['id'],
            topic=response.json()['topic'],
            date=date,
            start=start,
            end=end,
            timezone=response.json()['timezone'],
            password=response.json()['password'] if 'password' in data else '',
            agenda=data['agenda'] if 'agenda' in data else '',
            host_id=response.json()['host_id'],
            join_url=response.json()['join_url'],
            start_url=response.json()['start_url'],
            user_id=user_id,
            group_id=group_id
        )
        # 返回请求数据
        return JsonResponse(response.json())


class MeetingView(GenericAPIView, RetrieveModelMixin):
    """查询会议(id)"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()

    @swagger_auto_schema(operation_summary='查询会议')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MeetingDelView(GenericAPIView, DestroyModelMixin):
    """删除会议(mid)"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    # authentication_classes = (TokenAuthentication,)

    # 数据库与zoom-api删除同步，作逻辑删除
    @swagger_auto_schema(operation_summary='删除会议')
    def delete(self, request, *args, **kwargs):
        mid = kwargs.get('mid')
        url = "https://api.zoom.us/v2/meetings/{}".format(mid)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}
        response = requests.request("DELETE", url, headers=headers)
        if response.status_code == 204:
            Meeting.objects.filter(mid=mid).update(is_delete=1)
            return JsonResponse({"code": 204, "massege": "Delete successfully."})
        else:
            return JsonResponse(response.json())
