# Create your views here.
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from meetings.models import LoginItem, GroupItem, MeetingItem
from meetings.serializers import LoginSerializer, GroupSerializer, GroupsSerializer, MeetingSerializer, \
    MeetingsSerializer


class LoginView(GenericAPIView, CreateModelMixin):
    serializer_class = LoginSerializer
    queryset = LoginItem.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = GroupSerializer
    queryset = GroupItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class GroupsView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin):
    serializer_class = GroupsSerializer
    queryset = GroupItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class MeetingView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = MeetingSerializer
    queryset = MeetingItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class MeetingsView(GenericAPIView, RetrieveModelMixin, DestroyModelMixin):
    serializer_class = MeetingsSerializer
    queryset = MeetingItem.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# import app
# import requests
# from flask import request
# @app.route('/code', methods=["POST"])
# def get_code():
#     JSCODE = request.get_json()["code"]
#     encryptedData = request.get_json()["encryptedData"]
#     iv = request.get_json()["iv"]
#     APPID = "wx36f32371c57e97b0"
#     SECRET = "adcb8eea3b7ab910c696eabbb83ff207"
#     url = 'https://api.weixin.qq.com/sns/jscode2session?appid={appid}&secret={secret}&js_code={code}&grant_type=authorization_code'.format(appid=APPID,secret=SECRET,code=JSCODE)
#     res = requests.get(url)
#     openid = res.json().get('openid')
#     session_key = res.json().get('session_key')
#     pc = WXBizDataCrypt(APPID, session_key)
#     data = pc.decrypt(encryptedData, iv) #data中是解密的用户信息
#     return json_response(0,data=data)