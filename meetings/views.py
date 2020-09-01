import datetime
import json
import random
import requests
import logging
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework_simplejwt import authentication
from meetings.models import User, Group, Meeting, GroupUser
from meetings.permissions import MaintainerPermission, AdminPermission
from meetings.serializers import LoginSerializer, GroupsSerializer, MeetingSerializer, UsersSerializer, \
    UserSerializer, GroupUserAddSerializer, GroupSerializer, UsersInGroupSerializer, \
    UserGroupSerializer, MeetingListSerializer, GroupUserDelSerializer, UserInfoSerializer, \
    SigsSerializer


logger = logging.getLogger('log')


class LoginView(GenericAPIView, CreateModelMixin, ListModelMixin):
    """用户注册与授权登陆"""
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(operation_summary='用户注册与授权登陆')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class GroupsView(GenericAPIView, ListModelMixin):
    """查询所有SIG组的名称"""
    serializer_class = GroupsSerializer
    queryset = Group.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['group_name']

    @swagger_auto_schema(operation_summary='查询所有SIG组')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class SigsView(GenericAPIView, ListModelMixin):
    """查询所有SIG组的名称、首页、邮件列表、IRC频道及成员的nickname、gitee_name、avatar"""
    serializer_class = SigsSerializer
    queryset = Group.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class GroupView(GenericAPIView, RetrieveModelMixin):
    """查询单个SIG组"""
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    @swagger_auto_schema(operation_summary='查询单个SIG组')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UsersIncludeView(GenericAPIView, ListModelMixin):
    """查询所选SIG组的所有成员"""
    serializer_class = UsersInGroupSerializer
    queryset = User.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['nickname']

    @swagger_auto_schema(operation_summary='查询所选SIG组的所有成员')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            groupusers = GroupUser.objects.filter(group_id=self.kwargs['pk']).all()
            ids = [x.user_id for x in groupusers]
            user = User.objects.filter(id__in=ids)
            return user
        except KeyError:
            pass


class UsersExcludeView(GenericAPIView, ListModelMixin):
    """查询不在该组的所有成员"""
    serializer_class = UsersSerializer
    queryset = User.objects.all().order_by('nickname')
    filter_backends = [SearchFilter]
    search_fields = ['nickname']

    @swagger_auto_schema(operation_summary='查询不在该组的所有用户')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            groupusers = GroupUser.objects.filter(group_id=self.kwargs['pk']).all()
            ids = [x.user_id for x in groupusers]
            user = User.objects.filter().exclude(id__in=ids)
            return user
        except KeyError:
            pass


class UserGroupView(GenericAPIView, ListModelMixin):
    """查询该用户的SIG组以及该组的etherpad"""
    serializer_class = UserGroupSerializer
    queryset = GroupUser.objects.all()

    @swagger_auto_schema(operation_summary='查询该用户的SIG组以及该组的etherpad')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        try:
            usergroup = GroupUser.objects.filter(user_id=self.kwargs['pk']).all()
            return usergroup
        except KeyError:
            pass


class UserView(GenericAPIView, UpdateModelMixin):
    """更新用户gitee_name"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (AdminPermission,)

    @swagger_auto_schema(operation_summary='更新用户gitee_name')
    def put(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        gitee_name = request.data['gitee_name']

        if gitee_name:
            if User.objects.filter(gitee_name=gitee_name):
                logger.warning('The gitee_name {} has been taken'.format(gitee_name))
                return JsonResponse({'code': 400, 'msg': 'gitee_name重复'})
            if User.objects.filter(id=id, level=3):
                User.objects.filter(id=id).update(gitee_name=gitee_name)
            else:
                User.objects.filter(id=id).update(gitee_name=gitee_name, level=2)
        else:
            User.objects.filter(id=id).update(gitee_name=gitee_name, level=1)
        return self.update(request, *args, **kwargs)


class GroupUserAddView(GenericAPIView, CreateModelMixin):
    """SIG组批量新增成员"""
    serializer_class = GroupUserAddSerializer
    queryset = GroupUser.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (AdminPermission,)

    @swagger_auto_schema(operation_summary='SIG组批量新增成员')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupUserDelView(GenericAPIView, CreateModelMixin):
    """批量删除组成员"""
    serializer_class = GroupUserDelSerializer
    queryset = GroupUser.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (AdminPermission,)

    def post(self, request, *args, **kwargs):
        group_id = self.request.data.get('group_id')
        ids = self.request.data.get('ids')
        ids_list = [int(x) for x in ids.split('-')]
        GroupUser.objects.filter(group_id=group_id, user_id__in=ids_list).delete()
        return JsonResponse({'code': 204, 'msg': '删除成功'})


class MeetingsWeeklyView(GenericAPIView, ListModelMixin):
    """查询前后一周的所有会议"""
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.filter(is_delete=0)
    filter_backends = [SearchFilter]
    search_fields = ['topic', 'group_name']

    @swagger_auto_schema(operation_summary='查询前后一周的所有会议')
    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter((Q(
        date__gte=str(datetime.datetime.now() - datetime.timedelta(days=7))[:10]) & Q(
        date__lte=str(datetime.datetime.now() + datetime.timedelta(days=7))[:10]))).order_by('-date', 'start')
        return self.list(request, *args, **kwargs)


class MeetingsDailyView(GenericAPIView, ListModelMixin):
    """查询本日的所有会议"""
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.filter(is_delete=0)

    @swagger_auto_schema(operation_summary='查询本日的所有会议')
    def get(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(date=str(datetime.datetime.now())[:10]).order_by('start')
        return self.list(request, *args, **kwargs)


class MeetingView(GenericAPIView, RetrieveModelMixin):
    """查询会议(id)"""
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.filter(is_delete=0)

    @swagger_auto_schema(operation_summary='查询会议')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class MeetingDelView(GenericAPIView, DestroyModelMixin):
    """删除会议(mid)"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (MaintainerPermission,)

    @swagger_auto_schema(operation_summary='删除会议')
    def delete(self, request, *args, **kwargs):
        mid = kwargs.get('mid')
        try:
            url = "https://api.zoom.us/v2/meetings/{}".format(mid)
            headers = {
                "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}
            requests.request("DELETE", url, headers=headers)
        except Exception:
            pass
        Meeting.objects.filter(mid=mid).update(is_delete=1)
        logger.info('{} has canceled the meeting which mid was {}'.format(request.user.gitee_name, mid))
        return JsonResponse({"code": 204, "massege": "Delete successfully."})


class UserInfoView(GenericAPIView, RetrieveModelMixin):
    """查询本机用户的level和gitee_name"""
    serializer_class = UserInfoSerializer
    queryset = User.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        if user_id != request.user.id:
            logger.warning('user_id did not match.')
            logger.warning('user_id:{}, request.user.id:{}'.format(user_id, request.user.id))
            return JsonResponse({"code": 400, "massage": "错误操作，信息不匹配！"})
        return self.retrieve(request, *args, **kwargs)


class MeetingsDataView(GenericAPIView, ListModelMixin):
    """网页日历数据"""
    serializer_class = MeetingsDataSerializer
    queryset = Meeting.objects.filter(is_delete=0).order_by('start')

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).values()
        tableData = []
        date_list = []
        for query in queryset:
            date_list.append(query.get('date'))
        date_list = sorted(list(set(date_list)))
        for date in date_list:
            tableData.append(
                {
                'date': date,
                'timeData': [{
                    'id': meeting.id,
                    'group_name': meeting.group_name,
                    'startTime': meeting.start,
                    'endTime': meeting.end,
                    'duration': int(meeting.end.split(':')[0]) - int(meeting.start.split(':')[0]) if meeting.end.split(':')[1] == '00' else int(meeting.end.split(':')[0]) - int(meeting.start.split(':')[0]) + 1,
                    'duration_time': meeting.start.split(':')[0] + ':00' + '-' + meeting.end.split(':')[0] + ':00' if meeting.end.split(':')[1] == '00' else meeting.start.split(':')[0] + ':00' + '-' + str(int(meeting.end.split(':')[0]) + 1) + ':00',
                    'name': meeting.topic,
                    'creator': meeting.sponsor,
                    'detail': meeting.agenda,
                    'url': User.objects.get(id=meeting.user_id).avatar
                } for meeting in Meeting.objects.filter(is_delete=0, date=date)]
            })
        return Response({'tableData': tableData})


class SigMeetingsDataView(GenericAPIView, ListModelMixin):
    """网页SIG组日历数据"""
    serializer_class = MeetingsDataSerializer
    queryset = Meeting.objects.filter(is_delete=0).order_by('date', 'start')

    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('pk')
        queryset = self.filter_queryset(self.get_queryset()).values()
        tableData = []
        date_list = []
        for query in queryset:
            date_list.append(query.get('date'))
        date_list = sorted(list(set(date_list)))
        for date in date_list:
            tableData.append(
                {
                    'date': date,
                    'timeData': [{
                        'id': meeting.id,
                        'group_name': meeting.group_name,
                        'date': meeting.date,
                        'startTime': meeting.start,
                        'endTime': meeting.end,
                        'duration': int(meeting.end.split(':')[0]) - int(meeting.start.split(':')[0]) if meeting.end.split(':')[1] == '00' else int(meeting.end.split(':')[0]) - int(meeting.start.split(':')[0]) + 1,
                        'duration_time': meeting.start.split(':')[0] + ':00' + '-' + meeting.end.split(':')[0] + ':00' if meeting.end.split(':')[1] == '00' else meeting.start.split(':')[0] + ':00' + '-' + str(int(meeting.end.split(':')[0]) + 1) + ':00',
                        'name': meeting.topic,
                        'creator': meeting.sponsor,
                        'detail': meeting.agenda,
                        'url': User.objects.get(id=meeting.user_id).avatar
                    } for meeting in Meeting.objects.filter(is_delete=0, group_id=group_id, date=date)]
                })
        return Response({'tableData': tableData})


class MeetingsView(GenericAPIView, CreateModelMixin):
    """创建会议"""
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (MaintainerPermission,)

    @swagger_auto_schema(operation_summary='创建会议')
    def post(self, request, *args, **kwargs):
        import time
        t1 = time.time()
        host_dict = settings.MEETING_HOSTS
        # 获取data
        data = self.request.data
        date = data['date']
        start = data['start']
        end = data['end']
        user_id = request.user.id
        group_id = data['group_id']
        if start >= end:
            logger.warning('The end time must be greater than the start time.')
            return JsonResponse({'code': 1001, 'massage': '请输入正确的结束时间'})
        start_search = str(int(start.split(':')[0]) - 1) + ':00'
        end_search = str(int(end.split(':')[0]) + 1) + ':00'
        # 查询待创建的会议与现有的预定会议是否冲突
        meetings = Meeting.objects.filter(is_delete=0, date=date, start__gte=start_search, end__lte=end_search).values()
        try:
            for meeting in meetings:
                print('meeting: {}'.format(meeting))
                host_id = meeting.host_id
                del host_dict[host_id]
        except Exception:
            logger.info('当天此时段无host占用')
        if len(host_dict) == 0:
            logger.warning('暂无可用host')
            return JsonResponse({'code': 1000, 'massage': '暂无可用host,请前往官网查看预定会议'})
        # 从过滤后的host_dict中随机生成一个host
        print('host_dict: {}'.format(host_dict))
        host = random.choice(list(host_dict.values()))
        t2 = time.time()
        print('get host waste time: {}'.format(t2-t1))
        # start_time拼接
        if int(start.split(':')[0]) >= 8:
            start_time = date + 'T' + str(int(start.split(':')[0]) - 8) + ':00:00Z'
        else:
            d = datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=1)
            date = datetime.datetime.strftime(d, '%Y-%m-%d %H%M%S')[:10]
            start_time = date + 'T' + str(int(start.split(':')[0]) + 16) + ':00:00Z'
        # 计算duration
        duration = (int(end.split(':')[0]) - int(start.split(':')[0])) * 60 + (
                int(end.split(':')[1]) - int(start.split(':')[1]))
        # 准备好调用zoom api的data
        new_data = {}
        new_data['start_time'] = start_time
        new_data['duration'] = duration
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        url = "https://api.zoom.us/v2/users/{}/meetings".format(host)
        # 发送post请求，创建会议
        response = requests.post(url, data=json.dumps(new_data), headers=headers).json()
        # 数据库生成数据
        Meeting.objects.create(
            mid=response['id'],
            topic=data['topic'],
            sponsor=data['sponsor'],
            group_name=data['group_name'],
            date=date,
            start=start,
            end=end,
            etherpad=data['etherpad'],
            emaillist=data['emaillist'] if 'emaillist' in data else '',
            timezone=response['timezone'],
            agenda=data['agenda'] if 'agenda' in data else '',
            host_id=response['host_id'],
            join_url=response['join_url'],
            start_url=response['start_url'],
            user_id=user_id,
            group_id=group_id
        )
        logger.info('{} has created a meeting which mid is {}.'.format(data['sponsor'], response['id']))
        # 返回请求数据
        resp = {'code': 201, 'massage': '创建成功'}
        meeting = Meeting.objects.get(mid=response['id'])
        resp['id'] = meeting.id
        t3 = time.time()
        print('total waste: {}'.format(t3-t1))
        return JsonResponse(resp)

