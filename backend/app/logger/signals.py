import base64
import hashlib
import hmac
import math

import requests
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from app.logger.models import AlarmTalkLog, EmailLog, PhoneLog, PushLog

# from firebase_admin import messaging
# from sdk.api.message import Message
# from sdk.exceptions import CoolsmsException


@receiver(post_save, sender=EmailLog)
def send_email(sender, instance, created, *args, **kwargs):
    if created:
        url = f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages"
        data = {
            "from": settings.MAILGUN_FROM_EMAIL,
            "to": [instance.to],
            "subject": instance.title,
            "html": instance.body,
        }
        response = requests.post(url=url, data=data, auth=("api", settings.MAILGUN_API_KEY))
        if not response.ok:
            instance.status = "F"
        else:
            instance.status = "S"
        instance.save()


@receiver(post_save, sender=PhoneLog)
def send_sms(sender, instance, created, *args, **kwargs):
    if created:
        api_key = settings.COOLSMS_API_KEY
        api_secret = settings.COOLSMS_API_SECRET
        # 문자 전송
        data = {
            "from": settings.COOLSMS_FROM_PHONE,
            "to": instance.to,
            "text": instance.body,
        }

        message = Message(api_key, api_secret, use_http_connection=True)
        try:
            response = message.send(data)
            if "error_list" in response:
                instance.fail_reason = str(response)
            if response["success_count"]:
                instance.status = "S"
            else:
                instance.status = "F"
                instance.fail_reason = str(response)

        except CoolsmsException as e:
            instance.status = "F"
            instance.fail_reason = e.msg
        instance.save()


@receiver(post_save, sender=AlarmTalkLog)
def send_alarmtalk(sender, instance, created, *args, **kwargs):
    alarm_id = settings.ALARMTALK_ID
    client_id = settings.ALARMTALK_CLIENT_ID
    client_secret = bytes(settings.ALARMTALK_CLIENT_SECRET, "utf-8")

    sms_uri = f"/alarmtalk/v2/services/{alarm_id}/messages"
    url = f"https://sens.apigw.ntruss.com{sms_uri}"
    timestamp = str(int(timezone.now().timestamp() * 1000))
    hash_str = f"POST {sms_uri}\n{timestamp}\n{client_id}"

    digest = hmac.new(client_secret, msg=hash_str.encode("utf-8"), digestmod=hashlib.sha256).digest()
    d_hash = base64.b64encode(digest).decode()
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": client_id,
        "x-ncp-apigw-signature-v2": d_hash,
    }

    data = {
        "plusFriendId": "신고로",
        "templateCode": instance.template_code,
        "messages": [
            {
                "to": instance.to,
                "content": instance.body,
                "buttons": [
                    {
                        "type": "string",
                        "name": "string",
                        "linkMobile": "string",
                        "linkPc": "string",
                        "schemeIos": "string",
                        "schemeAndroid": "string",
                    }
                ],
                "useSmsFailover": True,
            }
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    if response.ok:
        instance.status = "S"
    else:
        print(response.text)
        instance.status = "F"
    instance.save()


# @receiver(post_save, sender=PushLog)
# def send_push(sender, instance, created, *args, **kwargs):
#     if created:
#         token_set = instance.user.device_set.values_list('token', flat=True)
#         for i in range(math.ceil(len(token_set) / 500)):
#             message = messaging.MulticastMessage(
#                 tokens=token_set[500*i:500*(i+1)],
#                 notification=messaging.Notification(
#                     title=instance.title,
#                     body=instance.body,
#                 ),
#             )
#             response = messaging.send_multicast(message)
#             if response.failure_count > 0:
#                 responses = response.responses
#                 failed_tokens = []
#                 for idx, resp in enumerate(responses):
#                     if not resp.success:
#                         failed_tokens.append(token_set[idx])
#                 print(failed_tokens)
