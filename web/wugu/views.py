import os
import random

from alipay import AliPay
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, permissions, status
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView

from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin, DestroyModelMixin, \
    RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt import authentication
from rest_framework_simplejwt.views import TokenViewBase

from pj5 import settings
from wugu.filters import GoodsThirdClassFilter
from wugu.models import UserInfo, GoodsSpecs, GoodsFirst, GoodsSecond, Cart, OrderInfo, UserPreference, IndexCarousel, \
    Tips, OrderAddress, GoodsDetailImages, OrderGoods, ComposedGoods
from wugu.serializers import RegisterSerializer, PhoneCodeSerializer, \
    GoodsCollocationSerializer, GoodsFirstListSerializer, GoodsSecondListSerializer, PersonalCenterSerializer, \
    OrderSerializer, CartCutSerializer, PaySerializer, PayResultSerializer, \
    UserPreferenceSerializer, IndexCarouselSerializer, TipsSerializer, OrderAddressSerializer, \
    CheckSerializer, TokenLoginSerializer, ChangeUserInfoSerializer, \
    CartSerialzer, CartDetailSerialzer, GoodsDetailSerializer, OrderCreatSerialzer, \
    OrderAddressManageSerializer, OrderGoodsSerializer, OrderInfoDeleteSerializer, ComposedGoodsDetailSerializer, \
    ComposedGoodsSerializer, GoodsSerializer, SearchSerialzer
from wugu.tests import send_msg


# 校验手机验证码
class CheckView(GenericAPIView, ListModelMixin, CreateModelMixin):
    serializer_class = CheckSerializer
    queryset = UserInfo.objects.all()

    @swagger_auto_schema(operation_summary='校验验证码', operation_id='验证')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        phone = serializer.data['phone']
        cache_code = cache.get(phone)
        if cache_code != serializer.data['phone_code']:
            raise serializers.ValidationError('验证码错误', code='code_error')
        # UserInfo.objects.create(phone=serializer.data['phone'])


class RegisterView(GenericAPIView, CreateModelMixin):
    '''注册'''
    serializer_class = RegisterSerializer
    queryset = UserInfo.objects.all()

    @swagger_auto_schema(operation_summary='提交注册信息', operation_id='注册')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    # def perform_create(self, serializer):
    #     UserInfo.objects.create(username=serializer.data['username'], password=make_password(serializer.data['password']),
    #                             phone=cache.get('phone'), email=serializer.data['email'])
    #     serializer.save()


# 五谷小知识
class TipsView(GenericAPIView, ListModelMixin):
    serializer_class = TipsSerializer
    queryset = Tips.objects.all()

    @swagger_auto_schema(operation_summary='访问页面', operation_id='五谷小知识页面')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 杂粮优搭配
class GoodsCollocationView(GenericAPIView, ListModelMixin):
    serializer_class = GoodsCollocationSerializer
    queryset = GoodsSpecs.objects.all()

    @swagger_auto_schema(operation_summary='访问页面', operation_id='杂粮优搭配页面')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 一类商品列表(含二类)
class GoodsFirstListView(GenericAPIView, ListModelMixin):
    serializer_class = GoodsFirstListSerializer
    queryset = GoodsFirst.objects.all()

    @swagger_auto_schema(operation_summary='查看具体一类商品', operation_id='一类商品列表')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 二类商品列表(含三类)
class GoodsSecondListView(GenericAPIView, ListModelMixin):
    serializer_class = GoodsSecondListSerializer
    queryset = GoodsSecond.objects.all()

    @swagger_auto_schema(operation_summary='查看具体二类商品', operation_id='二类商品列表')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 商品列表
class GoodsView(GenericAPIView, ListModelMixin):
    serializer_class = GoodsSerializer
    queryset = GoodsSpecs.objects.all()

    @swagger_auto_schema(operation_summary='查看商品列表', operation_id='商品列表')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 商品详情
class GoodsDetailView(GenericAPIView, RetrieveModelMixin):
    serializer_class = GoodsDetailSerializer
    queryset = GoodsSpecs.objects.all()

    @swagger_auto_schema(operation_summary='查看具体商品', operation_id='商品详情')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.retrieve(request, *args, **kwargs)


# 组合商品列表
class ComposedGoodsView(GenericAPIView, ListModelMixin):
    serializer_class = ComposedGoodsSerializer
    queryset = ComposedGoods.objects.all()

    @swagger_auto_schema(operation_summary='查看组合商品', operation_id='组合商品')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 组合商品详情
class ComposedGoodsDetailView(GenericAPIView, RetrieveModelMixin):
    serializer_class = ComposedGoodsDetailSerializer
    queryset = ComposedGoods.objects.all()

    @swagger_auto_schema(operation_summary='查看具体组合商品', operation_id='组合商品详情')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.retrieve(request, *args, **kwargs)


# 加入购物车
class AddToCartView(GenericViewSet, ListModelMixin, CreateModelMixin):
    queryset = Cart.objects.all()
    serializer_class = CartSerialzer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    # def get_object(self):
    #     return self.request.user

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'list':
            return CartDetailSerialzer
        else:
            return CartSerialzer


# 购物车删改
class CartCutView(GenericViewSet, UpdateModelMixin, DestroyModelMixin):
    serializer_class = CartCutSerializer
    queryset = Cart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.pk)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


# 个人中心页面
class PersonalCenterView(GenericAPIView, RetrieveModelMixin):
    serializer_class = PersonalCenterSerializer
    queryset = UserInfo.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(operation_summary='访问页面', operation_id='个人中心')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.retrieve(request, *args, **kwargs)


# 订单页面
class OrderView(GenericAPIView, ListModelMixin):
    serializer_class = OrderSerializer
    queryset = OrderGoods.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.pk)

    @swagger_auto_schema(operation_summary='查询订单', operation_id='订单详情')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 支付页面
class PayView(GenericAPIView, ListModelMixin):
    serializer_class = PaySerializer
    queryset = Cart.objects.all()
    # ==================================单独认证==================================
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    @swagger_auto_schema(operation_summary='', operation_id='支付页面')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 支付成功/失败页面
class PayResultView(GenericAPIView, ListModelMixin):
    serializer_class = PayResultSerializer
    queryset = Cart.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    @swagger_auto_schema(operation_summary='', operation_id='支付成功/失败页面')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 短信验证
class PhoneCodeView(GenericViewSet, CreateModelMixin):
    serializer_class = PhoneCodeSerializer

    def perform_create(self, serializer):
        phone = serializer.validated_data['phone']
        num_code = random.randint(1000, 9999)
        cache.set(phone, num_code, 300)
        print("电话号码：{}".format(phone))
        print("验证码：{}".format(num_code))
        result = send_msg(phone, num_code)
        if not result:
            raise serializers.ValidationError('验证码发送失败!', code='send_error')


# 用户偏好
class UserPreferenceView(ListCreateAPIView):
    serializer_class = UserPreferenceSerializer
    queryset = UserPreference.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    @swagger_auto_schema(operation_summary='访问页面', operation_id='用户偏好')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='提交信息', operation_id='用户偏好')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 首页轮播
class IndexCarouselView(GenericAPIView, ListModelMixin):
    serializer_class = IndexCarouselSerializer
    queryset = IndexCarousel.objects.all()

    @swagger_auto_schema(operation_summary='查询轮播图片', operation_id='首页轮播')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)


# 收货地址
class OrderAddressView(ListCreateAPIView):
    serializer_class = OrderAddressSerializer
    queryset = OrderAddress.objects.all()

    @swagger_auto_schema(operation_summary='访问页面', operation_id='订单地址')
    def get(self, request, *args, **kwargs):
        '''解释说明'''
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='添加信息', operation_id='订单地址')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 收货地址管理(增删改查)
class OrderAddressDetailView(GenericAPIView, UpdateModelMixin, DestroyModelMixin):
    serializer_class = OrderAddressManageSerializer
    queryset = OrderAddress.objects.all()

    @swagger_auto_schema(operation_summary='移除收货地址', operation_id='收货地址')
    def delete(self, request, *args, **kwargs):
        '''解释说明'''
        return self.destroy(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary='修改收货地址', operation_id='收货地址')
    def put(self, request, *args, **kwargs):
        '''解释说明'''
        return self.update(request, *args, **kwargs)


# 自定义token
class TokenLoginView(TokenViewBase):
    serializer_class = TokenLoginSerializer


# 修改个人信息
class ChangeUserInfoView(GenericAPIView, RetrieveModelMixin, UpdateModelMixin):
    serializer_class = ChangeUserInfoSerializer
    queryset = UserInfo.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(operation_summary='修改个人信息', operation_id='个人信息')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


# 创建订单
class OrderGoodsView(GenericViewSet, ListModelMixin, CreateModelMixin):
    queryset = OrderGoods.objects.all()
    serializer_class = OrderGoodsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    # def get_object(self):
    # return self.request.user

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderGoodsSerializer
        return OrderCreatSerialzer


# 订单信息详情
class OrderInfoDeleteView(GenericAPIView, DestroyModelMixin):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoDeleteSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.JWTAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.pk)

    @swagger_auto_schema(operation_summary='移除收货地址', operation_id='收货地址')
    def delete(self, request, *args, **kwargs):
        '''解释说明'''
        return self.destroy(request, *args, **kwargs)


# 搜索
class GoodsGetListView(GenericAPIView, ListModelMixin):
    queryset = GoodsSpecs.objects.all()
    serializer_class = SearchSerialzer
    filter_backends = [DjangoFilterBackend]
    filter_class = GoodsThirdClassFilter
    # search_fields = ['goods_name']

    @swagger_auto_schema(operation_summary='名字', operation_id='name')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


# 支付宝
def pay(request):
    order_id = request.POST.get("order_id")
    # 创建用于进行支付宝支付的工具对象
    key_path = os.path.join(settings.BASE_DIR, "alipay_key")
    private_key_string = open(os.path.join(key_path, "private_key")).read()
    public_key_string = open(os.path.join(key_path, "public_key")).read()
    alipay = AliPay(
        appid=settings.APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_string=private_key_string,
        alipay_public_key_string=public_key_string,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        sign_type="RSA2",  # RSA 或者 RSA2
        debug=True  # 默认False  配合沙箱模式使用
    )

    # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_id,
        total_amount=str(1000),  # 将Decimal类型转换为字符串交给支付宝
        subject="测试订单",
        return_url="http://192.168.110.47:8080/static/pages/cart.html",
        notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
    )

    # 让用户进行支付的支付宝页面网址
    url = settings.APP_GETAWAY + "?" + order_string

    return JsonResponse({"code": 0, "message": "请求支付成功", "url": url})


