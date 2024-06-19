# only POST method
SCHEDULE = dict(
    schedule_name={
        "path": "/cron/test/",
        "cron": "* * * * ? *",  # 분 시 일 월 요일 년
    },
)
