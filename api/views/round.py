import datetime

from django.utils import timezone
from api.models import Round
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from api.serializers.round import RoundGeneralSerializer, RoundChallengeSerializer
from api.repositories.round import RoundRepository

# Infra Repositories
repository: RoundRepository = RoundRepository(Round)


class RoundListAPIView(APIView):  # 列出所有回合

    @swagger_auto_schema(
        operation_summary="Get all rounds",
        operation_description="Get all rounds",
        responses={
            200: RoundChallengeSerializer(many=False),
            204: "No Content",
            404: "Not Found",
        },
    )
    def get(self, request):
        # 比較當前時間進行到哪一個回合
        round_instance = repository.getCurrentRound()
        if round_instance:
            # 標註該 Round 已經進行過了
            round_instance.is_valid = True
            round_instance.save()
            serializer = RoundChallengeSerializer(round_instance)
            return Response(serializer.data)
        # 檢查是否所有回合結束
        elif not repository.checkValidRoundExists():
            return Response(
                None,
                status=status.HTTP_204_NO_CONTENT,
            )
        # 檢查是否沒有開放回合
        elif not round_instance:
            return Response(
                None,
                status=status.HTTP_404_NOT_FOUND,
            )


class RoundAPIView(generics.RetrieveAPIView):
    queryset = repository.find_all()
    serializer_class = RoundGeneralSerializer
