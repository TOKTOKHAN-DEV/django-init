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
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.utils.safestring import mark_safe


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
            path("log/info/", wrap(self.log_info_view), name="log_info"),
            path("log/error/", wrap(self.log_error_view), name="log_error"),
            path("log/dashboard/", wrap(self.log_dashboard_view), name="log_dashboard"),
            path("api/log/info/", wrap(self.log_info_api_view), name="log_info_api"),
            path("api/log/error/", wrap(self.log_error_api_view), name="log_error_api"),
            path("api/log/dashboard/", wrap(self.log_dashboard_api_view), name="log_dashboard_api_view"),
        ]
        urls += super().get_urls()
        return urls

    def log_dashboard_view(self, request):
        context = dict(super().each_context(request))
        return TemplateResponse(request, "admin/log/dashboard.html", context)

    def log_info_view(self, request):
        context = dict(super().each_context(request))
        return TemplateResponse(request, "admin/log/info.html", context)

    def log_error_view(self, request):
        context = dict(super().each_context(request))
        return TemplateResponse(request, "admin/log/error.html", context)

    def __get_cw_dash_board_data(
        self,
        log_type,
        log_stream_list,
    ):
        log_data = []
        client = boto3.client("logs", region_name="ap-northeast-2")

        for log_stream in log_stream_list:
            try:
                response = client.get_log_events(
                    logGroupName=f"{settings.PROJECT_NAME}/{settigns.APP_ENV}/{log_type}",
                    logStreamName=f"web-{log_stream}",
                    limit=100,
                    startFromHead=False,
                )

                log_data.extend([event for event in response["events"] if response["events"]])

            except ClientError as error:
                print(f"ERROR : {error}")
                continue
        return log_data

    def __get_cw_data(self, log_stream, log_token, log_type):
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

    """
    아래는 Template에서 호출하는 API
    """

    def log_info_api_view(self, request, *args, **kwargs):
        log_info_data_list = self.__get_cw_data(
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
        log_error_data_list = self.__get_cw_data(
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

    def log_dashboard_api_view(self, request, *arg, **kwargs):
        log_stream_list = []

        current_date = timezone.now().date()
        std_date = current_date - datetime.timedelta(days=7)

        while std_date <= current_date:
            log_stream_list.append(std_date.strftime("%Y-%m-%d"))
            std_date += datetime.timedelta(days=1)

        log_dashboard_data_list = self.__get_cw_dash_board_data(
            "info", log_stream_list
        ) + self.__get_cw_dash_board_data("error", log_stream_list)

        response = []
        for event in log_dashboard_data_list:
            if "HTTP" in event["message"] and "monitoring" not in event["message"]:
                message = event["message"].split(" ")
                response.append(
                    {
                        "timestamp": datetime.datetime.fromtimestamp(event["timestamp"] / 1000).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "method": message[1] if type(message) == list else None,
                        "status_code": message[2] if type(message) == list else None,
                        "execution_time": float(message[3].strip("[]").strip("s")) if type(message) == list else None,
                        "path": message[4] if type(message) == list else None,
                        "message": message[-1] if type(message) == list else message,
                    }
                )

            elif "HTTP" not in event["message"] and "monitoring" not in event["message"]:

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

        return JsonResponse(
            data={
                "statusData": preprocessed_status_code_list,
                "executionData": preprocessed_execution_data_list,
            }
        )
