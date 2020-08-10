from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from meetings.models import Group, Meeting, User


class GroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class GroupsSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class MeetingSerializer(ModelSerializer):
    end_time = serializers.CharField(label='会议结束时间', max_length=255)

    class Meta:
        model = Meeting
        fields = ['meeting_id', 'topic', 'start_time', 'end_time', 'timezone', 'password', 'agenda', 'etherpad',
                  'host_id', 'join_url', 'start_url']


class MeetingsSerializer(ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


