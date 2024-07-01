import datetime
import os
from api.model.submission import Submission
from api.models import Challenge
from api.models import Team
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.submission import (
    SubmissionGeneralSerializer,
    SubmissionCreateSerializer,
)
from api.repositories.submission import SubmissionRepository
from api.repositories.challenge import ChallengeRepository
from judge import judge_submission

# Infra Repositories
repository: SubmissionRepository = SubmissionRepository(Submission)
challengeRepository: ChallengeRepository = ChallengeRepository(Challenge)

class SubmissionAPIView(APIView):

    @swagger_auto_schema(
        request_body=SubmissionCreateSerializer,
        responses={200: SubmissionGeneralSerializer},
    )
    def post(self, request):  # 上傳程式碼
        serializer = SubmissionCreateSerializer(data=request.data)
        now = datetime.datetime.now()
        serializer.is_valid(raise_exception=True)
        print(f'request data: {request.data}\n\n\n')

        # Retrieve the challenge object
        challenge_id = serializer.validated_data["challenge"].id
        team_id = serializer.validated_data["team"].id
        try:
            challenge = challengeRepository.get_by_id(challenge_id)
        except Challenge.DoesNotExist:
            return Response({"message": "Challenge not found"}, status=status.HTTP_404_NOT_FOUND)

        last_submission = repository.findNewestSubmissionByTeamId(request.data["team"])
        if last_submission is None:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        diff_time = now.timestamp() - last_submission.time.timestamp()
        if diff_time < 5:
            return Response(
                {"message": "Submission too fast"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Create Submission
        serializer.save()
        submission = repository.getLastSubmission()
        submission_id = submission.id
        image_url = challenge.image_url.url
        # Judge Answer
        code = serializer.data.get("code")

        drawing_template_path = f"judge_dir/drawing_code_template.py"
        main_drawing_path = f"media/code/main_drawing_template.py"
        template_revise_path = f"media/code/drawing_{submission_id}.py"
        
        code_path = f"media/code/{submission_id}.py"
        if os.path.isfile(code_path):
            # Remove the file
            os.remove(code_path)
        os.makedirs(os.path.dirname(code_path), exist_ok=True) # 建立資料夾

        with open (code_path, "w") as f:
            f.write(code)
        
        # result path is the path to the user drawing PNG file
        result_path = f"media/result/{challenge_id}/{submission_id}.png"
        if os.path.isfile(result_path):
            # Remove the file
            os.remove(result_path)
        os.makedirs(os.path.dirname(result_path), exist_ok=True) # 建立資料夾
        score, similarity, word_count, execution_time = judge_submission(
                        code_path, image_url, result_path, team_id, 
                        drawing_template_path, main_drawing_path, 
                        template_revise_path, submission_id)
        # Complete Judge
        print(f'score: {score}, similarity: {similarity}, word_count: {word_count}, execution_time: {execution_time}\n\n')
        submission.score = score
        submission.fitness = similarity
        submission.word_count = word_count
        submission.execute_time = datetime.timedelta(seconds=execution_time)
        submission.status = "success"
        submission.save()
        return Response(
            SubmissionGeneralSerializer(submission).data,
            status=status.HTTP_200_OK,
        )


class SubmissionChallengeTeamAPIView(APIView):

    @swagger_auto_schema(
        operation_summary="List submission by team and challenge",
        operation_description="List submission by team/challenge id",
        manual_parameters=[
            openapi.Parameter(
                "challenge_id",
                openapi.IN_PATH,
                description="The ID of the challenge",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "team_id",
                openapi.IN_PATH,
                description="The ID of the team",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: SubmissionGeneralSerializer},
    )
    def get(self, request, challenge_id: int, team_id: int):
        submissions = Submission.objects.filter(
            challenge__id=challenge_id, team__id=team_id
        ).order_by("-time")
        return Response(
            SubmissionGeneralSerializer(submissions, many=True).data,
            status=status.HTTP_200_OK,
        )


class SubmissionChallengeTeamMaxAPIView(APIView):
    @swagger_auto_schema(
        operation_summary="get highest score submission by team and challenge",
        operation_description="get highest score submission by team/challenge id",
        manual_parameters=[
            openapi.Parameter(
                "challenge_id",
                openapi.IN_PATH,
                description="The ID of the challenge",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "team_id",
                openapi.IN_PATH,
                description="The ID of the team",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: SubmissionGeneralSerializer},
    )
    def get(self, request, challenge_id: int, team_id: int):
        submissions = repository.findMaxScoreSubmissionByChallengeIdAndTeamId(
            challenge_id=challenge_id, team_id=team_id
        )
        return Response(
            SubmissionGeneralSerializer(submissions).data,
            status=status.HTTP_200_OK,
        )


class SubmissionTeamAPIView(APIView):
    def get(self, request, team_id:int): # 取得隊伍的所有提交
        submissions = repository.findAllSubmissionByTeamId(team_id=team_id)
        return Response(SubmissionGeneralSerializer(submissions, many=True).data, status=status.HTTP_200_OK)
