# Create your views here.
import json
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from meetings.models import LoginItem, GroupItem, MeetingItem
from meetings.serializers import LoginSerializer, GroupSerializer, GroupsSerializer, MeetingSerializer, \
    MeetingsSerializer
import requests
from django.conf import settings
from django.http import JsonResponse


class LoginView(View):
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
                nickname = nickname,
                avatar = avatar,
                gender = gender,
                status = 1
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
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
        }
        response = requests.get("https://api.zoom.us/v2/users/genedna@hey.com/meetings", headers=headers)
        return JsonResponse(response.json())

    def post(self, request, *args, **kwargs):
        headers = {
            "content-type": "application/json",
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)
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
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}

        response = requests.request("GET", url, headers=headers)
        return JsonResponse({"data": response.json()})

    def delete(self, request, *args, **kwargs):
        meeting_id = kwargs.get('meeting_id')
        url = "https://api.zoom.us/v2/meetings/{}".format(meeting_id)
        headers = {
            "authorization": "Bearer {}".format(settings.ZOOM_TOKEN)}
        response = requests.request("DELETE", url, headers=headers)
        if response.status_code == 204:
            return JsonResponse({"code": 204, "massege": "Delete successfully."})
        else:
            return JsonResponse(response.json())