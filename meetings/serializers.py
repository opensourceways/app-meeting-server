from rest_framework.serializers import ModelSerializer
from meetings.models import LoginItem, GroupItem, MeetingItem


class LoginSerializer(ModelSerializer):
    class Meta:
        model = LoginItem
        fields = '__all__'


class GroupSerializer(ModelSerializer):
    class Meta:
        model = GroupItem
        fields = '__all__'


class GroupsSerializer(ModelSerializer):
    class Meta:
        model = GroupItem
        fields = '__all__'


class MeetingSerializer(ModelSerializer):
    class Meta:
        model = MeetingItem
        fields = '__all__'


class MeetingsSerializer(ModelSerializer):
    class Meta:
        model = MeetingItem
        fields = '__all__'