import requests
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework import serializers, permissions
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.tokens import RefreshToken
from meetings.models import Group, User, Meeting, GroupUser


class GroupUserSerializer(ModelSerializer):
    class Meta:
        model = GroupUser
        fields = '__all__'


# 批量添加成员
class GroupUserAddSerializer(ModelSerializer):
    ids = serializers.CharField(max_length=255, write_only=True)
    group_id = serializers.CharField(max_length=255, write_only=True)
    authentication_classes = (authentication.JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    class Meta:
        model = GroupUser
        fields = ['group_id', 'ids']

    def validate_ids(self, value):
        try:
            list_ids = value.split('-')
        except:
            raise serializers.ValidationError('输入格式有误！,[1-2-3]', code='code_error')
        return list_ids

    def create(self, validated_data):
        users = User.objects.filter(id__in=validated_data['ids'])
        group_id = Group.objects.filter(id=validated_data['group_id']).first()
        try:
            for id in users:
                groupuser = GroupUser.objects.create(group_id=group_id.id, user_id=int(id.id))
            return groupuser
        except:
            raise serializers.ValidationError('创建失败！', code='code_error')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['msg'] = u'添加成功'
        return data


class GroupsSerializer(ModelSerializer):
    groupuser_set = GroupUserSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'group_name', 'home_page', 'app_detail_page', 'email', 'etherpad', 'description', 'groupuser_set']


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UsersSerializer(ModelSerializer):
    groupuser_set = GroupUserSerializer( many=True, read_only=True)
    class Meta:
        model = User
        fields = ['id', 'nickname', 'avatar', 'gitee_name', 'groupuser_set']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'gitee_name']


class MeetingSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['mid', 'topic', 'date', 'start', 'end', 'agenda', 'etherpad', 'join_url']

        extra_kwargs = {
            'mid': {'read_only': True},
            'join_url': {'read_only': True},
        }


class LoginSerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=128, write_only=True)
    access = serializers.CharField(label='请求密钥', max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['code', 'access']
        extra_kwargs = {
            'access': {'read_only': True}
        }

    def create(self, validated_data):
        try:
            res = self.context["request"].data
            code = res['code']
            if not code:
                raise serializers.ValidationError('需要code', code='code_error')
            r = requests.get(
                url='https://api.weixin.qq.com/sns/jscode2session?',
                params={
                    'appid': settings.APP_CONF['appid'],
                    'secret': settings.APP_CONF['secret'],
                    'js_code': code,
                    'grant_type': 'authorization_code'
                }
            ).json()

            openid = r['openid']
            if openid is None:
                raise serializers.ValidationError('未获取到openid', code='code_error')
                # return JsonResponse(resp)
            session_key = r['session_key']
            # 判断openid是否在数据库中，有则直接返回openid，session_key，没的话先在数据库创建记录再返回数据
            nickname = res['userInfo']['nickName'] if 'nickName' in res['userInfo'] else ''
            avatar = res['userInfo']['avatarUrl'] if 'avatarUrl' in res['userInfo'] else ''
            gender = res['userInfo']['gender'] if 'gender' in res['userInfo'] else 0
            user = User.objects.filter(openid=openid).first()
            # 如果user不存在，数据库创建user
            if not user:
                user = User.objects.create(
                    nickname=nickname,
                    avatar=avatar,
                    gender=gender,
                    status=1,
                    password=make_password(openid),
                    openid=openid)

            User.objects.update(
                nickname=nickname,
                avatar=avatar,
                gender=gender)
            return user
        except:
            raise serializers.ValidationError('非法参数', code='code_error')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['user_id'] = instance.id
        data['level'] = instance.level
        data['access'] = str(refresh.access_token)
        return data
