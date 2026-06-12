import os
from datetime import timedelta


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    raw = os.getenv(name, default)
    return [item.strip() for item in raw.split(",") if item.strip()]


def configure(
    namespace,
    *,
    service_name,
    base_dir,
    local_apps,
    identity_service=False,
):
    # Ham nay nhan globals() cua tung service va gan cau hinh Django dung chung.
    # Nho vay moi service chi can truyen ten service va app local, khong phai copy settings dai.
    debug = env_bool("DJANGO_DEBUG", False)
    namespace["BASE_DIR"] = base_dir
    namespace["SECRET_KEY"] = os.getenv("DJANGO_SECRET_KEY", f"dev-{service_name}-secret")
    namespace["DEBUG"] = debug
    namespace["ALLOWED_HOSTS"] = env_list("DJANGO_ALLOWED_HOSTS", "*")
    namespace["ROOT_URLCONF"] = "config.urls"
    namespace["WSGI_APPLICATION"] = "config.wsgi.application"
    namespace["ASGI_APPLICATION"] = "config.asgi.application"
    namespace["LANGUAGE_CODE"] = "en-us"
    namespace["TIME_ZONE"] = os.getenv("TIME_ZONE", "UTC")
    namespace["USE_I18N"] = True
    namespace["USE_TZ"] = True
    namespace["DEFAULT_AUTO_FIELD"] = "django.db.models.BigAutoField"
    namespace["SERVICE_NAME"] = service_name
    namespace["SERVICE_HTTP_TIMEOUT"] = int(os.getenv("SERVICE_HTTP_TIMEOUT", "5"))
    namespace["JWT_SIGNING_KEY"] = os.getenv("JWT_SIGNING_KEY", namespace["SECRET_KEY"])
    namespace["JWT_ALGORITHM"] = os.getenv("JWT_ALGORITHM", "HS256")

    installed_apps = ["django.contrib.contenttypes", "corsheaders", "rest_framework"]
    middleware = [
        "django.middleware.security.SecurityMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
    ]

    if identity_service:
        # Identity service la noi tao user that va phat JWT, nen can full Django auth/admin.
        installed_apps = [
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "corsheaders",
            "rest_framework",
            "rest_framework_simplejwt",
        ]
        middleware = [
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]
        namespace["AUTH_USER_MODEL"] = "accounts.User"
        namespace["TEMPLATES"] = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ]
        namespace["AUTH_PASSWORD_VALIDATORS"] = [
            {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
            {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
            {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
            {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
        ]
        namespace["SIMPLE_JWT"] = {
            "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))),
            "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
            "ALGORITHM": namespace["JWT_ALGORITHM"],
            "SIGNING_KEY": namespace["JWT_SIGNING_KEY"],
            "USER_ID_FIELD": "id",
            "USER_ID_CLAIM": "user_id",
        }
        default_authentication = (
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        )
    else:
        # Cac service con lai khong luu user local; chung chi verify JWT va tao request.user tu claims.
        default_authentication = (
            "ecommerce_common.authentication.ServiceJWTAuthentication",
        )

    namespace["INSTALLED_APPS"] = installed_apps + local_apps
    namespace["MIDDLEWARE"] = middleware
    namespace["REST_FRAMEWORK"] = {
        "DEFAULT_AUTHENTICATION_CLASSES": default_authentication,
        "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": int(os.getenv("PAGE_SIZE", "50")),
        "UNAUTHENTICATED_USER": None,
    }

    if env_bool("DJANGO_TEST_SQLITE", False):
        namespace["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    else:
        namespace["DATABASES"] = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("POSTGRES_DB", f"{service_name}_db"),
                "USER": os.getenv("POSTGRES_USER", "ecommerce"),
                "PASSWORD": os.getenv("POSTGRES_PASSWORD", "ecommerce"),
                "HOST": os.getenv("POSTGRES_HOST", f"{service_name}-db"),
                "PORT": os.getenv("POSTGRES_PORT", "5432"),
                "CONN_MAX_AGE": int(os.getenv("POSTGRES_CONN_MAX_AGE", "60")),
            }
        }

    namespace["STATIC_URL"] = "static/"
    namespace["CORS_ALLOWED_ORIGINS"] = env_list(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    namespace["CORS_ALLOW_CREDENTIALS"] = env_bool("CORS_ALLOW_CREDENTIALS", False)
    namespace["SERVICE_URLS"] = {
        # Ten logical service -> URL noi bo trong Docker network. Cac view dung map nay de goi service khac.
        "catalog": os.getenv("CATALOG_SERVICE_URL", "http://catalog-service:8000"),
        "customer": os.getenv("CUSTOMER_SERVICE_URL", "http://customer-service:8000"),
        "inventory": os.getenv("INVENTORY_SERVICE_URL", "http://inventory-service:8000"),
        "pricing": os.getenv("PRICING_SERVICE_URL", "http://pricing-service:8000"),
        "order": os.getenv("ORDER_SERVICE_URL", "http://order-service:8000"),
        "payment": os.getenv("PAYMENT_SERVICE_URL", "http://payment-service:8000"),
        "shipping": os.getenv("SHIPPING_SERVICE_URL", "http://shipping-service:8000"),
        "search": os.getenv("SEARCH_SERVICE_URL", "http://search-service:8000"),
        "recommendation": os.getenv("RECOMMENDATION_SERVICE_URL", "http://recommendation-service:8000"),
        "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000"),
    }
