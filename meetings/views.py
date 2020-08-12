import json, random
from django.views import View
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework_simplejwt.settings import api_settings
from meetings.models import Group, Meeting, User
from meetings.serializers import GroupSerializer, GroupsSerializer, MeetingSerializer, MeetingsSerializer
import requests
from django.conf import settings
from django.http import JsonResponse


class LoginView(View):
    # 通过前端传的code换取openid，session_key
    def get(self, request, *args, **kwargs):
        resp = {}
        res = request.GET
        code = request.GET['code']
        if not code:
            resp['message'] = '需要code'
            return JsonResponse(resp)
        r = requests.get(
            url='https://api.weixin.qq.com/sns/jscode2session?',
            params={
                'appid': settings.APP_CONF['appid'],
                'secret': settings.APP_CONF['secret'],
                'js_code': code,
                'grant_type': 'authorization_code'
            }
        ).json()
        openid = None
        if openid in r:
            openid = r['openid']
        if openid is None:
            resp['massage'] = '未获取到openid'
            return JsonResponse(resp)
        session_key = r['session_key']

        # 判断openid是否在数据库中，有则直接返回openid，session_key，没的话先在数据库创建记录再返回数据
        nickname = res['nickname'] if 'nickname' in res else ''
        avatar = res['avatarUrl'] if 'avatarUrl' in res else ''
        gender = res['gender'] if 'gender' in res else 1
        user = User.objects.filter(openid=openid).first()
        if not user:
            User.objects.create(
                nickname=nickname,
                avatar=avatar,
                gender=gender,
                status=1
            )
        # 添加token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        return JsonResponse({
            'message': 'success',
            'token': token,
            'openid': openid,
            'session_key': session_key
        })


class GroupsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = GroupsSerializer
    queryset = Group.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MeetingsView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all().filter(is_delete=0)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # 调用zoom-api查询所有会议
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        res = requests.get("https://api.zoom.us/v2/users/genedna@hey.com/meetings", headers=headers)
        # 将查询出的所有会议的id放入一个list
        meetings_id_list = []
        for meeting in res.json()['meetings']:
            meetings_id_list.append(meeting['id'])
        # 遍历meetings_id_list，用meeting_id查询单个会议具体信息，若该会议处于开启状态，则查出该会议对应的host，并从MEETING_HOSTS中排除掉
        for meeting_id in meetings_id_list:
            url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
            headers = {
                "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

            response = requests.request("GET", url, headers=headers)
            if response.json()['status'] == 'started':
                del settings.MEETING_HOSTS[response['host_id']]
                meetings_id_list.remove(meeting_id)
        if len(meetings_id_list) == 0:
            return JsonResponse({'code': 1000, 'massage': '无可用host'})
        # 随机取一个可用的host
        random.shuffle(meetings_id_list)
        meeting_id = meetings_id_list[0]
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

        response = requests.request("GET", url, headers=headers)
        host_email = settings.MEETING_HOSTS[response.json()['host_id']]
        # 发送post请求，创建会议
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        data = self.request.data
        url = "https://api.zoom.us/v2/users/{}/meetings".format(host_email)
        response = requests.post(url, data=json.dumps(data), headers=headers)

        # 数据库生成数据
        Meeting.objects.create(
            meeting_id=response.json()['id'],
            topic=response.json()['topic'],
            start_time=response.json()['start_time'],
            end_time=data['end_time'],
            timezone=response.json()['timezone'],
            password=data['password'] if 'password' in data else None,
            agenda=data['agenda'] if 'agenda' in data else None,
            join_url=response.json()['join_url'],
            start_url=response.json()['start_url']
        )
        # 返回请求数据
        return JsonResponse(response.json())


class MeetingView(GenericAPIView, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = MeetingsSerializer
    queryset = Meeting.objects.all()

    # 因本接口含所有会议信息，故不查询数据库
    def get(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

        response = requests.request("GET", url, headers=headers)
        return JsonResponse(response.json())

    # 数据库与zoom-api删除同步，作逻辑删除
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


