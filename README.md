# #{PROJECT_NAME} [![](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/) [![](https://img.shields.io/badge/django-4.2-green.svg)](https://www.python.org/downloads/) [![](https://img.shields.io/badge/drf-3.14-red.svg)](https://www.python.org/downloads/)  

## Root Directory Structure
```
├── .github              # github action directory
├── .idea                # pycharm config directory
└── backend              # django project root directory
```


## Backend Directory Structure
```
└── backend
    ├── api              # django api directory
    ├── app              # django app directory
    ├── config           # django config directory
    └── templates        # django template directory
```


## Package
- [requirements.txt](./backend/requirements.txt)


## Set AWS Profile
AWS Secret Manager, S3 Role을 가진 IAM Profile 등록  
mkdir ~/.aws  
vi ~/.aws/config
```
[profile #{PROJECT_NAME}]
aws_access_key_id=**
aws_secret_access_key=**
region = ap-northeast-2
```


## Set Environments
- 파이참 사용 시 (`terminal`, `django console`, `python console` 모두 환경변수 등록 됨)
  ```
  # __PROJECT_ROOT__
  cp .idea/workspace.temp.xml .idea/workspace.xml
  ```
- 그 외 IDE
  ```
  AWS_DEFAULT_PROFILE=#{PROJECT_NAME}
  DJANGO_SETTINGS_MODULE=config.settings.local
  ```


## Install Virtual Environment & Dependency
```
# __PROJECT_ROOT__/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```


## Create Dummy Data
```
python manage.py dummy [app_name.model_name] -n 10
```


## Run Server
```
python manage.py runserver 0:8000
```


## API Document
- http://api.localhost:8000/swagger/


# CI/CD Pipeline
![CI/CD](./.github/CICD.jpeg)
