from api.models import Team
from rest_framework import serializers


class TeamGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"
        read_only_fields = ("id",)


class TeamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name")


class TeamAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["token"]


class TeamAuthResponseSerializer(serializers.Serializer):
    status = serializers.BooleanField()
    team = TeamGeneralSerializer()
    access_token = serializers.CharField()
