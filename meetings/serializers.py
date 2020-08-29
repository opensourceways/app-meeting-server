import requests
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from meetings.models import Group, User, Meeting, GroupUser


logger = logging.getLogger('log')


class GroupUserAddSerializer(ModelSerializer):
    ids = serializers.CharField(max_length=255, write_only=True)
    group_id = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = GroupUser
        fields = ['group_id', 'ids']

    def validate_ids(self, value):
        try:
            list_ids = value.split('-')
        except Exception as e:
            logger.error('Invalid input.The ids should be like "1-2-3".')
            logger.error(e)
            raise serializers.ValidationError('输入格式有误！', code='code_error')
        return list_ids

    def create(self, validated_data):
        users = User.objects.filter(id__in=validated_data['ids'])
        group_id = Group.objects.filter(id=validated_data['group_id']).first()
        try:
            for id in users:
                groupuser = GroupUser.objects.create(group_id=group_id.id, user_id=int(id.id))
            return groupuser
        except Exception as e:
            logger.error('Failed to add maintainers to the group.')
            logger.error(e)
            raise serializers.ValidationError('创建失败！', code='code_error')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['code'] = 201
        data['msg'] = u'添加成功'
        return data


class GroupUserDelSerializer(ModelSerializer):
    ids = serializers.CharField(max_length=255, write_only=True)
    group_id = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = GroupUser
        fields = ['group_id', 'ids']


class GroupsSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'group_name']


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'gitee_name', 'avatar']


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'gitee_name']


class MeetingSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'topic', 'sponsor', 'group_name', 'date', 'start', 'end', 'etherpad', 'agenda', 'emaillist',
                  'user_id', 'group_id']
        extra_kwargs = {
            'mid': {'read_only': True},
            'join_url': {'read_only': True},
            'group_name': {'required': True}
        }


class MeetingListSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = ['id', 'user_id', 'topic', 'sponsor', 'group_name', 'date', 'start', 'end', 'agenda', 'etherpad', 'mid',
                  'join_url']


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
                logger.warning('Login without jscode.')
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
            if 'openid' not in r:
                logger.warning('Failed to get openid.')
                raise serializers.ValidationError('未获取到openid', code='code_error')
            openid = r['openid']
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
            else:
                User.objects.filter(openid=openid).update(
                    nickname=nickname,
                    avatar=avatar,
                    gender=gender)
            return user
        except Exception as e:
            logger.error('Invalid params')
            logger.error(e)
            raise serializers.ValidationError('非法参数', code='code_error')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['user_id'] = instance.id
        data['access'] = str(refresh.access_token)
        return data


class UsersInGroupSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'gitee_name', 'avatar']


class UserGroupSerializer(ModelSerializer):
    group_name = serializers.CharField(source='group.group_name', read_only=True)
    etherpad = serializers.CharField(source='group.etherpad', read_only=True)

    class Meta:
        model = GroupUser
        fields = ['group', 'group_name', 'etherpad']


class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['level', 'gitee_name']


class GroupUserSerializer(ModelSerializer):
    nickname = serializers.CharField(source='user.nickname', max_length=40, read_only=True)
    gitee_name = serializers.CharField(source='user.gitee_name', max_length=40, read_only=True)
    avatar = serializers.CharField(source='user.avatar', max_length=256, read_only=True)

    class Meta:
        model = GroupUser
        fields = ['user', 'nickname', 'gitee_name', 'avatar']


class SigsSerializer(ModelSerializer):
    groupuser_set = GroupUserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'group_name', 'home_page', 'maillist', 'irc', 'groupuser_set']
