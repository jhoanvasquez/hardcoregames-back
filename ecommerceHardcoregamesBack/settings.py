"""
Django settings for ecommerceHardcoregamesBack project.

Generated by 'django-admin startproject' using Django 4.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8cn@ply1603#h-4o9bvjbuehv186x7=wg0xqm)q6$s#h_*97xi'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'users',
    'products',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'ecommerceHardcoregamesBack.urls'

# CORS_ALLOWED_ORIGINS = {
#  'http://localhost:4200',
# }

# CORS_ALLOWED_ORIGIN_REGEXES = [
#     'http://localhost:4200',
# ]

CORS_ALLOW_METHODS = (
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
)

# CORS_ALLOW_HEADERS = (
#     "accept",
#     "authorization",
#     "content-type",
#     "user-agent",
#     "x-csrftoken",
#     "x-requested-with",
# )

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerceHardcoregamesBack.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hardcoregames',
        'USER': 'postgres',
        'PASSWORD': '#1998jhoan',
        'HOST': 'localhost',
        'DATABASE_PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-co'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

STATIC_URL_FILES = 'static/files/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SEND_EMAIL=os.getenv("SEND_EMAIL")
FROM_EMAIL="jhoan0498@gmail.com"
PASS_SMTP="bbcg cluw zlia hhui "
SUBJECT_EMAIL_FOR_TOKEN = "Código para cambio de contraseña HardCoreGames"
SUBJECT_EMAIL_FOR_SALE = "Confirmación de compra en HardCoreGames"
EMAIL_FOR_TOKEN = "<html>" \
                    "<body>" \
                        "<h2>Solicitud de nueva contraseña HardCoreGames</h2><br>" \
                        "<justify>Está recibiendo este correo electrónico porque se ha solicitado un cambio de contraseña para la cuenta de HardCoreGames. " \
                        "Su codigo de activacion para cambio de contraseña es:</justify> " \
                    "</body>" \
                  "</html>"

EMAIL_FOR_SALE = '<div style="max-width:560px;background-color:#f5f5f5;border-radius:5px;margin:40px auto;font-family:Open Sans,Helvetica,Arial;font-size:15px;color:#000000"> <div class="adM"> </div> <div style="font-weight:normal"> <div class="adM"> </div> <div style="text-align:center;font-weight:600;font-size:26px;padding:20px 0;padding-top:41px;padding-bottom:22px"><img src="https://firebasestorage.googleapis.com/v0/b/hardcoregames-3aa7e.appspot.com/o/HARDCORE%20GAMING%20Logotipo%20PNG.png?alt=media&token=2351374f-617b-47e8-9b60-667c3701bb5d" width="190" class="CToWUd" data-bit="iit"> </div> </div> <div style="padding:0 20px 20px 20px"> <hr style="border-color:#e0e0e0;border-width:1px"> <div style="padding:10px 0;text-align:justify;line-height:1.3"> <div style="font-size:19px;margin-bottom:30px">¡Hola!<br></div> <div id="body" style="margin-top: 8%;"> Hemos recibido tu compra, a continuación se detallan los datos de acceso necesarios para obetener tu producto: <hr style="border-color:#e0e0e0;border-width:1px"> </div> <!-- <div style="padding:20px 0 0 0;text-align:center"> <a style="background:#2168f5;color:#fff;padding:4px 8px;text-decoration:none;border-radius:3px;letter-spacing:0.3px" href="https://web.plattaforma.com/autenticacion/iniciar-sesion" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://web.plattaforma.com/autenticacion/iniciar-sesion&amp;source=gmail&amp;ust=1700761454173000&amp;usg=AOvVaw0fVv_gii5BusId7t4exOzS">Ir a licitación</a> </div> --> <div style="margin-top:40px"> Equipo HardCoreGames </div> </div> <hr style="border-color:#e0e0e0;border-width:1px"> <div style="padding:12px;text-align:left"> <div style="font-size:13px"> <div style="font-size:15px;font-weight:bold;margin-bottom:5px">Contacta a soporte:</div> <a href="mailto:soporte@plattaforma.com" style="text-decoration:none;color:black;display:flex;float:left" target="_blank"> <img style="width:20px" src="https://ci4.googleusercontent.com/proxy/bN9cvP1P6fpjNlf1RWVks6gbzAJFexZgOiQitHCz1R6iSMlLqFULZ5n--57oj39eObIWv_0cwM21CjhFt2IZqWbTwOdCquh6GcNOJ0nKQUo=s0-d-e1-ft#https://backend.plattaforma.com/images/iconos/email-black.png" class="CToWUd" data-bit="iit">&nbsp;hardcoregaming453@gmail.com </a> <a style="float:left;text-decoration:none;color:black">&nbsp;|&nbsp;</a> <a href="https://wa.me/50766094872" style="text-decoration:none;color:black;display:flex" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://wa.me/50766094872&amp;source=gmail&amp;ust=1700761454173000&amp;usg=AOvVaw0vROaGkqYwpmeagr8k1FP4"> <img style="width:20px" src="https://ci6.googleusercontent.com/proxy/YIHg9Jq-iFEJYfxml9vCTYAnNKH9wWzmjPZSCGZE3MCovRXxisN_qwG5bfjssweETXYSOCxy2h79G_xXomw76yHkyAZQqnzkqu4zx3lo1KhrzvU=s0-d-e1-ft#https://backend.plattaforma.com/images/iconos/whatsapp-black.png" class="CToWUd" data-bit="iit">+57&nbsp;3167431812 </a> </div> <br> <!-- <div> <div style="font-weight:bold;margin-bottom:5px">Lleva a Plattaforma contigo</div> <a href="https://apps.apple.com/co/app/plattaforma/id6446603077" style="text-decoration:none" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://apps.apple.com/co/app/plattaforma/id6446603077&amp;source=gmail&amp;ust=1700761454173000&amp;usg=AOvVaw317EuiXQMO9eLxvBi63AuA"> <img style="width:128px;padding-right:5px" src="https://ci5.googleusercontent.com/proxy/QvSWpo-UrIu8Xok5OXxMtFwpv1vnJDtRCeUS4-PNCivcVODdFrbjPNhf3uUOxHxljPu_GUpX0x3qCaf2mwudbYyERRN0E1vx5ncbDsJz=s0-d-e1-ft#https://backend.plattaforma.com/images/iconos/app_store.png" class="CToWUd" data-bit="iit"> </a> <a href="https://play.google.com/store/apps/details?id=com.plattaforma.app" style="text-decoration:none" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://play.google.com/store/apps/details?id%3Dcom.plattaforma.app&amp;source=gmail&amp;ust=1700761454173000&amp;usg=AOvVaw2sFVvUEMwwu2R-bK0N3TRI"> <img style="width:128px;padding-left:5px" src="https://ci5.googleusercontent.com/proxy/tM0NE0VqxDhukwUVxWbfaxv30TvRnl-32ugy_CszikpeY9ZLZnYBTEwveJt4v5KiyIxGScLkfEmK2T77a03nXaQX6_T_oxZLuYlrQQUoTA=s0-d-e1-ft#https://backend.plattaforma.com/images/iconos/play_store.png" class="CToWUd" data-bit="iit"> </a> </div> --> <br> <div> Copyright 2023 </div> </div> <div class="yj6qo"></div> <div class="adL"></div> </div></div>'