import datetime
import json
import re
import statistics
import time
from collections import defaultdict
from functools import update_wrapper

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import AdminSite as DjangoAdminSite
from django.db.models import Count
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.safestring import mark_safe

from app.user.models import User

"""
================================================================
"""


def create_card_component(title, data, col):
    """
    대시보드 카드 컴포넌트 생성 함수

    :param title: 카드 제목
    :param data: 카드 데이터 ( 상수 )
    :param col: 카드의 열 크기 ( 최대 12 )
    :return:
    """
    return {
        "title": title,
        "component": {
            "kind": "CARD",
            "data": data,
            "col": col,
        },
    }


def create_pie_chart_component(title, data, col):
    """
    파이 차트 컴포넌트 생성 함수
    :param title: 차트 제목
    :param data: 차트 데이터
    :param col: 차트 열 크기 ( 최대 12 )
    :return:
    """
    return {
        "title": title,
        "component": {
            "kind": "PIE_CHART",
            "data": data,
            "col": col,
        },
    }


def get_cw_dash_board_data(log_type, log_stream_list):
    """
    서버 모니터링 대시보드 데이터 조회 함수

    :param log_type: 클라우드 와치 로그 타입 (info, error)
    :param log_stream_list: 로그 스트임 리스트
    :return:
    """
    log_data = []
    client = boto3.client("logs", region_name="ap-northeast-2")

    for log_stream in log_stream_list:
        try:
            response = client.get_log_events(
                logGroupName=f"{settings.PROJECT_NAME}/{settings.APP_ENV}/{log_type}",
                logStreamName=f"web-{log_stream}",
                limit=100,
                startFromHead=False,
            )

            log_data.extend([event for event in response["events"] if response["events"]])

        except ClientError as error:
            print(f"ERROR : {error}")
            continue
    return log_data


def get_cw_log_data(log_stream, log_token, log_type):
    """
    클라우드 와치 로그 데이터 조회

    :param log_stream: 로그 스트림
    :param log_token: 로그 조회 토큰
    :param log_type: 로그 타입 ( info, error )
    :return:
    """
    client = boto3.client("logs", region_name="ap-northeast-2")

    # # 로그 그룹 이름과 로그 스트림 이름을 지정
    log_group_name = f"{settings.PROJECT_NAME}/{settings.APP_ENV}/{log_type}"
    log_data = []

    try:
        if log_token:
            response = client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=f"web-{log_stream}",
                limit=100,
                startFromHead=False,
                nextToken=log_token,
            )

        else:
            response = client.get_log_events(
                logGroupName=log_group_name,
                logStreamName=f"web-{log_stream}",
                limit=100,
                startFromHead=False,
            )

        log_data.extend([event for event in response["events"] if response["events"]])

        return {
            "data": sorted(log_data, key=lambda x: x["timestamp"], reverse=True),
            "next_token": response["nextForwardToken"],
            "prev_token": response["nextBackwardToken"],
        }

    except ClientError as error:
        print(f"ERROR : {error}")
        return {
            "data": [],
            "next_token": None,
            "prev_token": None,
        }


def get_log_dashboard_data():
    log_stream_list = []

    current_date = timezone.now().date()
    std_date = current_date - datetime.timedelta(days=2)

    while std_date <= current_date:
        log_stream_list.append(std_date.strftime("%Y-%m-%d"))
        std_date += datetime.timedelta(days=1)

    log_dashboard_data_list = get_cw_dash_board_data("info", log_stream_list) + get_cw_dash_board_data(
        "error", log_stream_list
    )

    response = []
    for event in log_dashboard_data_list:
        if "HTTP" in event["message"] and "monitoring" not in event["message"] and "service" not in event["message"]:
            message = event["message"].split(" ")

            if "v1" not in message[4]:
                continue

            response.append(
                {
                    "timestamp": datetime.datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "method": message[1],
                    "status_code": message[2],
                    "execution_time": float(message[3].strip("[]").strip("s")),
                    "path": message[4].split("?")[0] if message[4].split("?") else message[4],
                    "message": message[-1],
                }
            )

        elif (
            "HTTP" not in event["message"]
            and "monitoring" not in event["message"]
            and "service" not in event["message"]
        ):

            path_match = re.search(r"Error: (.+)", event["message"])
            if path_match:
                path = path_match.group(1).strip()
            else:
                path = "Unknown"

            # Traceback 부분 추출
            traceback_match = re.search(r"Traceback.*?(\n\s*File .+)", event["message"], re.DOTALL)
            if traceback_match:
                traceback = traceback_match.group(1).strip()
            else:
                traceback = "Unknown"

            # 가공된 데이터 출력
            response.append(
                {
                    "message": traceback,
                    "path": path,
                    "timestamp": datetime.datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "method": None,
                    "status_code": "500",
                    "execution_time": None,
                }
            )

    # 상태코드 파이차트 데이터 Preprocessing
    status_code_data = defaultdict(list)
    [status_code_data[item.pop("status_code")].append(item) for item in response]

    # API 실행시간 Bar 차트 데이터 Preprocessing
    execution_data = defaultdict(list)
    [execution_data[item.pop("path")].append(item) for item in response]

    # 상태코드 차트 status Code로 GroupBy
    preprocessed_status_code_list = [
        {"statusCode": code, "data": len(data)} for code, data in status_code_data.items() if code
    ]

    # API 실행시간으로 GroupBy
    preprocessed_execution_data_list = [
        {
            "path": path,
            "data": statistics.mean([item.get("execution_time") for item in data if item.get("execution_time")]),
        }
        for path, data in execution_data.items()
        if path and any(item.get("execution_time") for item in data)
    ]

    return {"statusData": preprocessed_status_code_list, "executionData": preprocessed_execution_data_list}


def get_ecs_metrics(client, metric_name, service):
    cw_ecs_metrics_response = client.get_metric_statistics(
        Namespace="AWS/ECS",
        MetricName=metric_name,
        Dimensions=[
            {"Name": "ClusterName", "Value": f"{settings.PROJECT_NAME}-{settings.APP_ENV}-ecs-cluster"},
            {"Name": "ServiceName", "Value": service},
        ],
        StartTime=datetime.datetime.utcnow() - datetime.timedelta(hours=5),  # 조회 시작 시간 설정
        EndTime=datetime.datetime.utcnow(),  # 조회 종료 시간 설정
        Period=1200,  # 데이터 포인트 간격 (10분)
        Statistics=["Average", "Maximum", "Minimum"],  # 평균값 조회
        Unit="Percent",  # 사용률 단위 (퍼센트)
    )
    return [
        {
            "timestamp": (datapoint["Timestamp"] + datetime.timedelta(hours=9)).strftime("%H:%M"),
            "maxValue": round(datapoint["Maximum"], 2),
            "avgValue": round(datapoint["Average"], 2),
            "minValue": round(datapoint["Minimum"], 2),
        }
        for datapoint in cw_ecs_metrics_response["Datapoints"]
    ]

def get_ecs_cpu_usage_data():
    # ECS CPU 사용률 조회
    client = boto3.client("cloudwatch", region_name="ap-northeast-2")

    return {
        "ecsWebCpuData": sorted(get_ecs_metrics(client, "CPUUtilization", "web"), key=lambda d: d["timestamp"]),
        "ecsCeleryCpuData": sorted(get_ecs_metrics(client, "CPUUtilization", "celery"), key=lambda d: d["timestamp"]),
    }


def get_ecs_memory_usage_data():
    # ECS Memory 사용률 조회
    client = boto3.client("cloudwatch", region_name="ap-northeast-2")

    return {
        "ecsWebMemoryData": sorted(get_ecs_metrics(client, "MemoryUtilization", "web"), key=lambda d: d["timestamp"]),
        "ecsCeleryMemoryData": sorted(get_ecs_metrics(client, "MemoryUtilization", "celery"), key=lambda d: d["timestamp"]),
    }

"""
================================================
"""


class AdminSite(DjangoAdminSite):
    site_header = (
        mark_safe(
            f'<img src="{settings.STATIC_URL + settings.SITE_LOGO}" height="28" style="vertical-align: bottom;" />'
        )
        if settings.SITE_LOGO
        else f"{settings.SITE_NAME} 어드민"
    )
    site_url = settings.FRONTEND_URL

    def get_urls(self):
        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)

            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        urls = [
            path("service/dashboard/", wrap(self.service_dashboard_view), name="service_dashboard"),
            path("log/info/", wrap(self.log_info_view), name="log_info"),
            path("log/error/", wrap(self.log_error_view), name="log_error"),
            path("log/dashboard/", wrap(self.log_dashboard_view), name="log_dashboard"),
            path("log/info/api/", wrap(self.log_info_api_view), name="log_info_api"),
            path("log/error/api/", wrap(self.log_error_api_view), name="log_error_api"),
        ]
        urls += super().get_urls()
        return urls

    def get_component(self):
        return [
            create_card_component(title="총 사용자 수(명)", data=User.objects.count(), col=4),
            create_card_component(
                title="오늘 가입한 사용자 수(명)",
                data=User.objects.filter(date_joined__date=timezone.now().date()).count(),
                col=4,
            ),
            # create_pie_chart_component(
            #     title="금주 탈퇴 인원 나이대 비율",
            #     data=[
            #         {"label": "10대", "value": 120},
            #         {"label": "20대", "value": 50},
            #         {"label": "30대", "value": 44},
            #         {"label": "40대", "value": 25},
            #         {"label": "50대", "value": 13},
            #     ],
            #     col=4,
            # ),
        ]

    def service_dashboard_view(self, request):
        context = dict(super().each_context(request))
        context["ui_component"] = self.get_component()
        return TemplateResponse(request, "admin/service/dashboard.html", context)

    def log_dashboard_view(self, request):
        context = dict(super().each_context(request))

        context["log_dashboard_data"] = get_log_dashboard_data()
        context["ecs_cpu_usage_data"] = get_ecs_cpu_usage_data()
        context["ecs_memory_usage_data"] = get_ecs_memory_usage_data()
        return TemplateResponse(request, "admin/log/dashboard.html", context)

    def log_info_view(self, request):
        context = dict(super().each_context(request))
        return TemplateResponse(request, "admin/log/info.html", context)

    def log_error_view(self, request):
        context = dict(super().each_context(request))
        return TemplateResponse(request, "admin/log/error.html", context)

    """
    아래는 Template에서 호출하는 API
    """

    def log_info_api_view(self, request, *args, **kwargs):
        log_info_data_list = get_cw_log_data(
            log_stream=request.GET.get("startDate"),
            log_token=request.GET.get("logToken"),
            log_type="info",
        )

        response = {
            "data": [],
            "nextToken": log_info_data_list["next_token"],
            "prevToken": log_info_data_list["prev_token"],
        }

        for event in log_info_data_list["data"]:
            message = None
            if "HTTP" in event["message"] and "monitoring" not in event["message"]:
                message = event["message"].split(" ")

            elif "HTTP" not in event["message"] and "monitoring" not in event["message"]:
                try:
                    message = json.loads(event["message"])

                except json.JSONDecodeError as e:
                    message = event["message"]

            if message:
                response["data"].append(
                    {
                        "timestamp": datetime.datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "method": message[1] if type(message) == list else "-----",
                        "statusCode": message[2] if type(message) == list else "-----",
                        "executionTime": float(message[3].strip("[]").strip("s")) if type(message) == list else "-----",
                        "path": message[4] if type(message) == list else "-----",
                        "message": "-----" if type(message) == list else message,
                    }
                )
        return JsonResponse(data=response)

    def log_error_api_view(self, request, *args, **kwargs):
        log_error_data_list = get_cw_log_data(
            log_stream=request.GET.get("startDate"),
            log_token=request.GET.get("logToken"),
            log_type="error",
        )
        response = {
            "data": [],
            "nextToken": log_error_data_list["next_token"],
            "prevToken": log_error_data_list["prev_token"],
        }

        for event in log_error_data_list["data"]:
            path_match = re.search(r"Error: (.+)", event["message"])
            if path_match:
                path = path_match.group(1).strip()
            else:
                path = "Unknown"

            # Traceback 부분 추출
            traceback_match = re.search(r"Traceback.*?(\n\s*File .+)", event["message"], re.DOTALL)
            if traceback_match:
                traceback = traceback_match.group(1).strip()
            else:
                traceback = "Unknown"

            # 가공된 데이터 출력
            response["data"].append(
                {
                    "message": traceback,
                    "path": path,
                    "timestamp": datetime.datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "method": "-----",
                    "statusCode": "-----",
                    "executionTime": "-----",
                }
            )

        return JsonResponse(data=response)
