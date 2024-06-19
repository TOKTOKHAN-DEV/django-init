from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.common.permissions import IsCron


class CronView(APIView):
    permission_classes = [IsCron]

    def cron(self):
        raise NotImplemented("Not implemented yet")

    def post(self, request, *args, **kwargs):
        self.cron()
        return Response(status=status.HTTP_201_CREATED)
