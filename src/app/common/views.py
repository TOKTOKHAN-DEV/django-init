from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.views import exception_handler as default_exception_handler

from app.common.permissions import IsScheduler


def exception_handler(exc, context):
    response = default_exception_handler(exc, context)
    return response


class SchedulerView(APIView):
    permission_classes = [IsScheduler]

    def schedule(self):
        raise NotImplementedError("Not implemented yet")

    def post(self, request, *args, **kwargs):
        self.schedule()
        return Response(status=status.HTTP_201_CREATED)
