"""zoom_meetings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(openapi.Info(
    title="zoom_meetings",  # 在线文档标题
    default_version='v1',  # 在线文档版本
    description="The APIs are made for community meetings.",  # 在线文档描述
    terms_of_service="https://www.google.com/policies/terms/",  # 服务团队地址
    contact=openapi.Contact(email="contact@openeuler.org"),  # 邮箱联系
    license=openapi.License(name="BSD License"),  # 许可条款
),
    public=True,  # 是否是公共访问
    permission_classes=(permissions.AllowAny,),  # 访问权限，AllowAny：任何人都可以访问，
    # IsAuthenticated： 认证过后的用户才可以，
    # IsAdminUser：  超级用户才能访问
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('meetings.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),name='schema-redoc')
]
