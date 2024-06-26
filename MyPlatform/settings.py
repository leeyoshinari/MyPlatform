"""
Django settings for MyPlatform project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
import configparser
from pathlib import Path

import redis
import influxdb
from common.MinIOStorage import MinIOStorage
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

cfg = configparser.ConfigParser()
cfg.read(os.path.join(BASE_DIR, 'config.conf'), encoding='utf-8')

def get_config(key):
    return cfg.get('default', key, fallback=None)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-e-f8ypr2q9w4_-v-zx19+^4(7i!lp6yu)w!wvl%+bia-u5+_lk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

IS_ATIJMETER = int(get_config('isATIJMeter'))
IS_MONITOR = int(get_config('isMonitor'))
IS_PERF = int(get_config('isPerformanceTest'))
IS_NGINX = int(get_config('isNginxFlow'))
SAMPLING_INTERVAL = int(get_config('samplingInterval'))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'user',
    'channels',
    'shell',
    'monitor',
    'performance',
    'compressor',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'MyPlatform.mymiddleware.AccessAuthMiddleWare'
]

ROOT_URLCONF = 'MyPlatform.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'myFilter': 'templateFilter.MyFilter'
            }
        },
    },
]

WSGI_APPLICATION = 'MyPlatform.wsgi.application'
ASGI_APPLICATION = 'MyPlatform.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

if get_config('dbType') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': get_config('MysqlDatabase'),
            'USER': get_config('MysqlUserName'),
            'PASSWORD': get_config('MysqlPassword'),
            'HOST': get_config('MysqlHost'),
            'PORT': get_config('MysqlPort'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
GMT = int(get_config('GMT'))
USE_I18N = True
USE_L10N = True
USE_TZ = False
PAGE_SIZE = 20

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
PREFIX = get_config("prefix")
STATIC_URL = f'{PREFIX}/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles')]
COMPRESS_ENABLED = True
STATICFILES_FINDERS = {
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

EXCLUDE_URL = 'login|register|changePwd'

# log path
BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(levelname)s - [%(threadName)s:%(thread)d] - %(filename)s[line:%(lineno)d] - %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'default': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_LOG_DIR, "access.log"),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': int(get_config('backupCount')),
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default'],  # default, console
            'level': get_config('level'),
            'propagate': True,
        }
    },
}

# monitor or jmeter agent
HEARTBEAT = 12  # heart beat time, unit: second(s)
PERFORMANCE_EXPIRE = 604800  # performance test redis keys expire time, 7D

# The path of deploying agent
DEPLOY_PATH = get_config('deployPath')
# The collector-agent address
COLLECTOR_AGENT_ADDRESS = get_config('collectorAgentAddress')

# files
# files store local path
FILE_ROOT_PATH = os.path.join(BASE_DIR, 'static', 'files')
TEMP_PATH = os.path.join(BASE_DIR, 'static', 'temp')
FILE_STORE_TYPE = get_config('storeType')
FILE_URL = get_config('fileURL')
if not os.path.exists(TEMP_PATH):
    os.mkdir(TEMP_PATH)
if not os.path.exists(FILE_ROOT_PATH):
    os.mkdir(FILE_ROOT_PATH)

if FILE_STORE_TYPE == '1':
    MINIO_HOST = get_config('MinIOHost')
    MINIO_ACCESSKEY = get_config('MinIOAccessKey')
    MINIO_SECRETKEY = get_config('MinIOSecretKey')
    MINIO_CLIENT = MinIOStorage(MINIO_HOST, MINIO_ACCESSKEY, MINIO_SECRETKEY)

# Redis
REDIS_HOST = get_config('RedisHost')
REDIS_PORT = int(get_config('RedisPort'))
REDIS_PWD = get_config('RedisPassword')
REDIS_DB = int(get_config('RedisDB'))
REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DB, decode_responses=True)

# influxDB
INFLUX_HOST = get_config('InfluxHost')
INFLUX_PORT = get_config('InfluxPort')
INFLUX_USER_NAME = get_config('InfluxUserName')
INFLUX_PASSWORD = get_config('InfluxPassword')
INFLUX_DATABASE = get_config('InfluxDatabase')
INFLUX_EXPIRY_TIME = int(get_config('expiryTime'))
INFLUX_SHARD_DURATION = get_config('shardDuration')
INFLUX_CLIENT = influxdb.InfluxDBClient(INFLUX_HOST, INFLUX_PORT, INFLUX_USER_NAME, INFLUX_PASSWORD, INFLUX_DATABASE)
INFLUX_CLIENT.query(f'alter retention policy "autogen" on "{INFLUX_DATABASE}" duration '
                    f'{INFLUX_EXPIRY_TIME}d REPLICATION 1 SHARD DURATION {INFLUX_SHARD_DURATION} default;')

# Email
EMAIL_SMTP = get_config('SMTP')
EMAIL_SENDER_NAME = get_config('EmailSenderName')
EMAIL_SENDER_EMAIL = get_config('EmailSenderEmail')
EMAIL_PASSWORD = get_config('EmailPassword')
EMAIL_RECEIVER_NAME = get_config('EmailReceiverName')
EMAIL_RECEIVER_EMAIL = get_config('EmailReceiverEmail')
