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

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

IS_MITMPROXY = int(get_config('isMitmProxy'))
IS_MONITOR = int(get_config('isMonitor'))
IS_PERF = int(get_config('isPerformanceTest'))

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
    'mitm',
    'performance',
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

USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/
CONTEXT = get_config("context")
STATIC_URL = f'{CONTEXT}/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

EXCLUDE_URL = 'login|admin|Register|changePwd'

BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
if not os.path.exists(BASE_LOG_DIR):
    os.mkdir(BASE_LOG_DIR)

LOGGING = {
    'version': 1,  # 保留字
    'disable_existing_loggers': True,  # 禁用已经存在的logger实例
    # 日志文件的格式
    'formatters': {
        # 详细的日志格式
        'standard': {
            'format': '%(asctime)s - %(levelname)s - [%(threadName)s:%(thread)d] - %(filename)s[line:%(lineno)d] - %(message)s'
        },
    },
    # 过滤器
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # 处理器
    'handlers': {
        # 在终端打印
        'console': {
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',  #
            'formatter': 'standard'
        },
        # 默认的
        'default': {
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "access.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 5,  # 日志大小 10M
            'backupCount': int(get_config('backupCount')),  # 最多备份几个
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
       # 默认的logger应用如下配置
        'django': {
            'handlers': ['default'],  # 上线之后可以把'console'移除
            'level': get_config('level'),
            'propagate': True,  # 向不向更高级别的logger传递
        }
    },
}
# MitmProxy
REDIS_HOST = get_config('RedisHost')
REDIS_PORT = int(get_config('RedisPort'))
REDIS_PWD = get_config('RedisPassword')
REDIS_DB = int(get_config('RedisDB'))

# influxDB
INFLUX_HOST = get_config('InfluxHost')
INFLUX_PORT = get_config('InfluxPort')
INFLUX_USER_NAME = get_config('InfluxUserName')
INFLUX_PASSWORD = get_config('InfluxPassword')
INFLUX_DATABASE = get_config('InfluxDatabase')
INFLUX_EXPIRY_TIME = int(get_config('expiryTime'))
INFLUX_SHARD_DURATION = get_config('shardDuration')

# Email
EMAIL_SMTP = get_config('SMTP')
EMAIL_SENDER_NAME = get_config('EmailSenderName')
EMAIL_SENDER_EMAIL = get_config('EmailSenderEmail')
EMAIL_PASSWORD = get_config('EmailPassword')
EMAIL_RECEIVER_NAME = get_config('EmailReceiverName')
EMAIL_RECEIVER_EMAIL = get_config('EmailReceiverEmail')
