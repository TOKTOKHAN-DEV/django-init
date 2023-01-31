from rest_framework.generics import CreateAPIView

from api.v1.verifier.serializers import (
    EmailVerifierConfirmSerializer,
    EmailVerifierCreateSerializer,
    PhoneVerifierConfirmSerializer,
    PhoneVerifierCreateSerializer,
)


class EmailVerifierCreateView(CreateAPIView):
    """
    이메일 인증
    ---
    """

    serializer_class = EmailVerifierCreateSerializer


class EmailVerifierConfirmView(CreateAPIView):
    """
    이메일 인증 확인
    ---
    응답값의 token값으로 회원가입의 emailToken으로 사용
    """

    serializer_class = EmailVerifierConfirmSerializer


class PhoneVerifierCreateView(CreateAPIView):
    """
    휴대폰 인증
    ---
    """

    serializer_class = PhoneVerifierCreateSerializer


class PhoneVerifierConfirmView(CreateAPIView):
    """
    휴대폰 인증 확인
    ---
    응답값의 token값으로 회원가입의 phoneToken으로 사용
    """

    serializer_class = PhoneVerifierConfirmSerializer
