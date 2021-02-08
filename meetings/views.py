import datetime
import json
import math
import random
import requests
import logging
import time
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework_simplejwt import authentication
from meetings.models import User, Group, Meeting, GroupUser, Collect, Video, Record
from meetings.permissions import MaintainerPermission, AdminPermission
from meetings.serializers import LoginSerializer, GroupsSerializer, MeetingSerializer, UsersSerializer, \
    UserSerializer, GroupUserAddSerializer, GroupSerializer, UsersInGroupSerializer, \
    UserGroupSerializer, MeetingListSerializer, GroupUserDelSerializer, UserInfoSerializer, \
    SigsSerializer, MeetingsDataSerializer, AllMeetingsSerializer, CollectSerializer
from rest_framework.response import Response
from multiprocessing import Process
from meetings.send_email import sendmail
from rest_framework import permissions

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
    queryset = Group.objects.all().order_by('group_name')
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
        except:
            pass
        # 会议作软删除
        meeting = Meeting.objects.get(mid=mid)
        Meeting.objects.filter(mid=mid).update(is_delete=1)
        meeting_id = meeting.id
        mid = meeting.mid
        logger.info('{} has canceled the meeting which mid was {}'.format(request.user.gitee_name, mid))
        # 发送会议取消通知
        collections = Collect.objects.filter(meeting_id=meeting_id)
        if collections:
            access_token = self.get_token()
            topic = meeting.topic
            date = meeting.date
            start_time = meeting.start
            time = date + ' ' + start_time
            for collection in collections:
                user_id = collection.user_id
                user = User.objects.get(id=user_id)
                nickname = user.nickname
                openid = user.openid
                content = self.get_remove_template(openid, topic, time, mid)
                r = requests.post('https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={}'.format(access_token),
                                  data=json.dumps(content))
                if r.status_code != 200:
                    logger.error('status code: {}'.format(r.status_code))
                    logger.error('content: {}'.format(r.json()))
                else:
                    if r.json()['errcode'] != 0:
                        logger.warning('Error Code: {}'.format(r.json()['errcode']))
                        logger.warning('Error Msg: {}'.format(r.json()['errmsg']))
                        logger.warning('receiver: {}'.format(nickname))
                    else:
                        logger.info('meeting {} cancel message sent to {}.'.format(mid, nickname))
                # 删除收藏
                collection.delete()
        return JsonResponse({"code": 204, "message": "Delete successfully."})

    def get_remove_template(self, openid, topic, time, mid):
        if len(topic) > 20:
            topic = topic[:20]
        content = {
            "touser": openid,
            "template_id": "UpxRbZf8Z9QiEPlZeRCgp_MKvvqHlo6tcToY8fToK50",
            "page": "/pages/index/index",
            "miniprogram_state": "developer",
            "lang": "zh-CN",
            "data": {
                "thing1": {
                    "value": topic
                },
                "time2": {
                    "value": time
                },
                "thing4": {
                    "value": "会议{}已被取消".format(mid)
                }
            }
        }
        return content

    def get_token(self):
        appid = settings.APP_CONF['appid']
        secret = settings.APP_CONF['secret']
        url = 'https://api.weixin.qq.com/cgi-bin/token?appid={}&secret={}&grant_type=client_credential'.format(appid,
                                                                                                               secret)
        r = requests.get(url)
        if r.status_code == 200:
            try:
                access_token = r.json()['access_token']
                return access_token
            except KeyError as e:
                logger.error(e)
        else:
            logger.error(r.status_code, r.json())
            logger.error('fail to get access_token,exit.')
            sys.exit(1)


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
            return JsonResponse({"code": 400, "message": "错误操作，信息不匹配！"})
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
                    'duration': math.ceil(float(meeting.end.replace(':', '.'))) - math.floor(
                            float(meeting.start.replace(':', '.'))),
                    'duration_time': meeting.start.split(':')[0] + ':00' + '-' + str(
                            math.ceil(float(meeting.end.replace(':', '.')))) + ':00', 
                    'name': meeting.topic,
                    'creator': meeting.sponsor,
                    'detail': meeting.agenda,
                    'url': User.objects.get(id=meeting.user_id).avatar,
                    'join_url': meeting.join_url,
                    'meeting_id': meeting.mid,
                    'etherpad': meeting.etherpad,
                    'video_url': '' if not Record.objects.filter(mid=meeting.mid, platform='bilibili') else
                    Record.objects.filter(mid=meeting.mid, platform='bilibili').values()[0]['url']
                } for meeting in Meeting.objects.filter(is_delete=0, date=date)]
            })
        return Response({'tableData': tableData})


class SigMeetingsDataView(GenericAPIView, ListModelMixin):
    """网页SIG组日历数据"""
    serializer_class = MeetingsDataSerializer
    queryset = Meeting.objects.filter(is_delete=0).order_by('date', 'start')

    def get(self, request, *args, **kwargs):
        group_id = kwargs.get('pk')
        queryset = self.filter_queryset(self.get_queryset()).filter(group_id=group_id).filter((Q(
        date__gte=str(datetime.datetime.now() - datetime.timedelta(days=180))[:10]) & Q(
        date__lte=str(datetime.datetime.now() + datetime.timedelta(days=30))[:10]))).values() 
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
                        'duration': math.ceil(float(meeting.end.replace(':', '.'))) - math.floor(
                                float(meeting.start.replace(':', '.'))),
                        'duration_time': meeting.start.split(':')[0] + ':00' + '-' + str(
                                math.ceil(float(meeting.end.replace(':', '.')))) + ':00', 
                        'name': meeting.topic,
                        'creator': meeting.sponsor,
                        'detail': meeting.agenda,
                        'url': User.objects.get(id=meeting.user_id).avatar,
                        'join_url': meeting.join_url,
                        'meeting_id': meeting.mid,
                        'etherpad': meeting.etherpad,
                        'video_url': '' if not Record.objects.filter(mid=meeting.mid, platform='bilibili') else
                        Record.objects.filter(mid=meeting.mid, platform='bilibili').values()[0]['url']
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
        t1 = time.time()
        host_dict = settings.MEETING_HOSTS
        # 获取data
        data = self.request.data
        date = data['date']
        start = data['start']
        end = data['end']
        topic = data['topic']
        community = data['community'] if 'community' in data else 'openeuler'
        emaillist = data['emaillist'] if 'emaillist' in data else ''
        summary = data['agenda'] if 'agenda' in data else ''
        user_id = request.user.id
        group_id = data['group_id']
        record = data['record'] if 'record' in data else ''
        start_time = ' '.join([date, start])
        if start_time < datetime.datetime.now().strftime('%Y-%m-%d %H:%M'):
            logger.warning('The start time should not be earlier than the current time.')
            return JsonResponse({'code': 1005, 'message': '请输入正确的开始时间'})
        if start >= end:
            logger.warning('The end time must be greater than the start time.')
            return JsonResponse({'code': 1001, 'message': '请输入正确的结束时间'})
        start_search = datetime.datetime.strftime((datetime.datetime.strptime(start, '%H:%M') - datetime.timedelta(minutes=60)),
                                                          '%H:%M')
        end_search = datetime.datetime.strftime((datetime.datetime.strptime(end, '%H:%M') + datetime.timedelta(minutes=60)),
                                                        '%H:%M')
        # 查询待创建的会议与现有的预定会议是否冲突
        unavailable_host_id = []
        available_host_id = []
        meetings = Meeting.objects.filter(is_delete=0, date=date, start__gte=start_search, end__lte=end_search).values()
        try:
            for meeting in meetings:
                host_id = meeting['host_id']
                unavailable_host_id.append(host_id)
            logger.info('unavilable_host_id:{}'.format(unavailable_host_id))
        except KeyError:
            pass
        host_list = list(host_dict.keys())
        logger.info('host_list:{}'.format(host_list))
        for host_id in host_list:
            if host_id not in unavailable_host_id:
                available_host_id.append(host_id)
        logger.info('avilable_host_id:{}'.format(available_host_id))
        if len(available_host_id) == 0:
            logger.warning('暂无可用host')
            return JsonResponse({'code': 1000, 'message': '暂无可用host,请前往官网查看预定会议'})
        # 从available_host_id中随机生成一个host_id,并在host_dict中取出
        host_id = random.choice(available_host_id)
        host = host_dict[host_id]
        logger.info('host_id:{}'.format(host_id))
        logger.info('host:{}'.format(host))
        # start_time拼接
        if int(start.split(':')[0]) >= 8:
            start_time = date + 'T' + ':'.join([str(int(start.split(':')[0]) - 8), start.split(':')[1], '00Z'])
        else:
            d = datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=1)
            d2 = datetime.datetime.strftime(d, '%Y-%m-%d %H%M%S')[:10]
            start_time = d2 + 'T' + ':'.join([str(int(start.split(':')[0]) + 16), start.split(':')[1], '00Z'])
        # 计算duration
        duration = (int(end.split(':')[0]) - int(start.split(':')[0])) * 60 + (
                int(end.split(':')[1]) - int(start.split(':')[1]))
        # 准备好调用zoom api的data
        password = ""
        for i in range(6):
            ch = chr(random.randrange(ord('0'), ord('9') + 1))
            password += ch
        new_data = {}
        new_data['settings'] = {}
        new_data['start_time'] = start_time
        new_data['duration'] = duration
        new_data['topic'] = topic
        new_data['password'] = password
        new_data['settings']['waiting_room'] = False
        new_data['settings']['auto_recording'] = record
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        url = "https://api.zoom.us/v2/users/{}/meetings".format(host)
        # 发送post请求，创建会议
        response = requests.post(url, data=json.dumps(new_data), headers=headers)
        if response.status_code != 201:
            logger.info('code: {}, fail to create.'.format(response.status_code))
            return JsonResponse({'code': response.status_code, 'msg': 'Fail to create.'})
        response = response.json()

        # 发送email
        join_url = response['join_url']
        sig_name = data['group_name']
        toaddrs = emaillist
        
        p1 = Process(target=sendmail, args=(topic, date, start, join_url, sig_name, toaddrs, summary, record))
        p1.start() 

        # 数据库生成数据
        Meeting.objects.create(
            mid=response['id'],
            topic=data['topic'],
            community=community,
            sponsor=data['sponsor'],
            group_name=data['group_name'],
            date=date,
            start=start,
            end=end,
            etherpad=data['etherpad'],
            emaillist=emaillist,
            timezone=response['timezone'],
            agenda=data['agenda'] if 'agenda' in data else '',
            host_id=response['host_id'],
            join_url=response['join_url'],
            start_url=response['start_url'],
            user_id=user_id,
            group_id=group_id
        )
        logger.info('{} has created a meeting which mid is {}.'.format(data['sponsor'], response['id']))
        logger.info('meeting info: {},{}-{},{}'.format(date, start, end, topic))

        # 如果开启录制功能，则在Video表中创建一条数据
        if record == 'cloud':
            Video.objects.create(
                mid=response['id'],
                topic=data['topic'],
                community=community,
                group_name=data['group_name'],
                agenda=data['agenda'] if 'agenda' in data else ''
            )
            logger.info('meeting {} was created with auto recording.'.format(response['id']))

        # 返回请求数据
        resp = {'code': 201, 'message': '创建成功'}
        meeting = Meeting.objects.get(mid=response['id'])
        resp['id'] = meeting.id
        t3 = time.time()
        print('total waste: {}'.format(t3 - t1))
        return JsonResponse(resp)


class MyMeetingsView(GenericAPIView, ListModelMixin):
    """查询我创建的所有会议"""
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.all().filter(is_delete=0)
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    @swagger_auto_schema(operation_summary='查询我创建的所有会议')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Meeting.objects.filter(is_delete=0, user_id=self.request.user.id).order_by('-date', 'start')
        return queryset


class AllMeetingsView(GenericAPIView, ListModelMixin):
    """列出所有会议"""
    serializer_class = AllMeetingsSerializer
    queryset = Meeting.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['is_delete', 'group_name', 'sponsor', 'date', 'start', 'end']
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class CollectView(GenericAPIView, ListModelMixin, CreateModelMixin):  
    """收藏会议"""
    serializer_class = CollectSerializer
    queryset = Collect.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def post(self, request, *args, **kwargs):
        user_id = self.request.user.id
        meeting_id = self.request.data['meeting']
        Collect.objects.create(meeting_id=meeting_id, user_id=user_id)
        resp = {'code': 201, 'msg': 'collect successfully'}
        return JsonResponse(resp)

    def get_queryset(self):
        queryset = Collect.objects.filter(user_id=self.request.user.id)
        return queryset


class CollectDelView(GenericAPIView, DestroyModelMixin):
    """取消收藏"""
    serializer_class = CollectSerializer
    queryset = Collect.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Collect.objects.filter(user_id=self.request.user.id)
        return queryset


class MyCollectionsView(GenericAPIView, ListModelMixin):
    """我收藏的会议(列表)"""
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        user_id = self.request.user.id
        collection_lst = Collect.objects.filter(user_id=user_id).values_list('meeting', flat=True)
        queryset = Meeting.objects.filter(is_delete=0, id__in=collection_lst).order_by('-date', 'start')
        return queryset


class ParticipantsView(GenericAPIView, RetrieveModelMixin):
    """查询会议的参会者"""
    def get(self, request, *args, **kwargs):
        mid = kwargs.get('mid')
        try:
            url = "https://api.zoom.us/v2/past_meetings/{}/participants".format(mid)
            headers = {
                "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                return JsonResponse({'total_records': r.json()['total_records'], 'participants': r.json()['participants']})
            else:
                return JsonResponse(r.json())
        except Exception as e:
            logger.error(e)
            return JsonResponse({'msg': e})
