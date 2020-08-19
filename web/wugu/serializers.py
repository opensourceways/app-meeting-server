from random import Random
from time import strftime

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from wugu.models import UserInfo, GoodsSpecs, GoodsFirst, GoodsSecond, Cart, OrderInfo, UserPreference, IndexCarousel, \
    Tips, OrderAddress, GoodsImages, DiscountGoods, GoodsDetailImages, GoodsThirdImages, GoodsThirdDetailImages, \
    OrderGoods, ComposedGoods, ComposedGoodsImages


# 用户信息
class UserInfoSerializer(ModelSerializer):
    class Meta:
        model = UserInfo
        fields = '__all__'


# 短信验证码校验
class CheckSerializer(ModelSerializer):
    phone_code = serializers.IntegerField()

    class Meta:
        model = UserInfo
        fields = ['phone', 'phone_code']


# 手机号获取验证码
class PhoneCodeSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', max_length=11)

    def validate_phone(self, value):
        result = UserInfo.objects.filter(phone=value)
        if result:
            raise serializers.ValidationError('用户已注册!', code='code_error')
        return value


# 注册
class RegisterSerializer(ModelSerializer):
    access = serializers.CharField(label='请求密钥', max_length=255, read_only=True)
    refresh = serializers.CharField(label='刷新密码', max_length=255, read_only=True)
    phone_code = serializers.CharField(label='手机验证码', max_length=4, write_only=True)

    class Meta:
        model = UserInfo
        fields = ['phone', 'username', 'password', 'email', 'access', 'refresh', 'phone_code']

    def validate(self, attrs):
        code = cache.get(attrs['phone'])
        if str(code) != attrs['phone_code']:
            raise serializers.ValidationError('验证失败！')
        del attrs['phone_code']
        return attrs

    def validate_password(self, value):
        return make_password(value)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        refresh = RefreshToken.for_user(instance)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class PhoneTokenRefreshSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField()
        self.fields['phone_code'] = serializers.CharField()


class PhoneUserNameSerializer(serializers.Serializer):
    username = serializers.CharField(label='账号', max_length=10)

    def validate_username(self, value):
        result = UserInfo.objects.filter(username=value)
        if result is None:
            raise serializers.ValidationError('用户未注册!', code='no_register')
        return result[0].phone


# 杂粮优搭配
class GoodsCollocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSpecs
        fields = '__all__'


# 一类商品列表(含二类)
class GoodsFirstListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsFirst
        fields = '__all__'


# 二类商品列表(含二类)
class GoodsSecondListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSecond
        fields = ['goods_second_class']


# 购物车删、改
class CartCutSerializer(serializers.ModelSerializer):
    code = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'goods', 'goods_number', 'cart_generation_time', 'code']

    def get_code(self, obj):
        return 200

    # def validate(self, attrs):
    #     attrs['code'] = 200
    #     return attrs


# 个人中心
class PersonalCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'user_img']


# 支付
class PaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


# 支付后
class PayResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


# 用户偏好
class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = '__all__'


# 首页轮播
class IndexCarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexCarousel
        fields = '__all__'


# 五谷小知识
class TipsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tips
        fields = '__all__'


# 收货地址
class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = '__all__'


# 收货地址管理
class OrderAddressManageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = '__all__'


# 自定义token
class TokenLoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = UserInfo.objects.filter(Q(username=attrs['username']) | Q(phone=attrs['username']))

        if not user:
            raise serializers.ValidationError('用户不存在', code='user_error')
        elif not check_password(attrs['password'], user[0].password):
            raise serializers.ValidationError('密码错误', code='password_error')
        refresh = self.get_token(user[0])
        data = {}
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


# 修改个人信息
class ChangeUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'gender', 'email', ]


# 查询折扣价
class DiscountGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountGoods
        fields = ['discounted_price']


# 商品主图
class GoodsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsImages
        fields = ['goods_img']


# 商品三类展示图
class GoodsThirdImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsThirdImages
        fields = '__all__'


# 商品三类详情图
class GoodsThirdDetailImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsThirdDetailImages
        fields = '__all__'


class GoodsSecondSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsSecond
        fields = ['goods_second_class', ]


# 商品规格
class GoodsSpecsSerialzer(serializers.ModelSerializer):
    discountgoods_set = DiscountGoodsSerializer(many=True, read_only=True)
    goodsimages_set = GoodsImageSerializer(source='goods.goodsimages_set', many=True, read_only=True)
    goodssecond_set = GoodsSecondSerializer(source='goods.goodssecond_set', many=True, read_only=True)

    class Meta:
        model = GoodsSpecs
        fields = ['discountgoods_set', 'goodsimages_set', 'goods_specs', 'goods_title',
                  'goods_price', 'goods_introduction', 'goods_sale', 'goodssecond_set']


# 查询购物车列表
class CartDetailSerialzer(serializers.ModelSerializer):
    goods = GoodsSpecsSerialzer(many=False, read_only=True)

    # goods_sum_price = SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'goods', 'goods_number']

    # def get_goods_sum_price(self, obj):
    #     return '{:0.2f}'.format(float(obj.goods.goods_price) * obj.goods_number)


# 新增、+1 购物车
class CartSerialzer(serializers.Serializer):
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=GoodsSpecs.objects.all())
    goods_number = serializers.IntegerField(label='数量', default=1, min_value=1, error_messages={
        "min_value": "商品数量不能小于1",
        "required": "请选择购买数量"
    })

    def create(self, validated_data):
        goods = validated_data['goods']
        goods_number = validated_data['goods_number']
        existed = Cart.objects.filter(Q(goods=goods) & Q(user_id=self.context['request'].user.id))
        if existed:
            existed = existed[0]
            existed.goods_number += goods_number
            existed.user_id = self.context['request'].user.id
            existed.save()
        else:
            validated_data['user_id'] = self.context['request'].user.id
            existed = Cart.objects.create(**validated_data)
        return existed

    def update(self, instance, validated_data):
        instance.goods_number = validated_data['goods_number']
        instance.save()
        return instance


# 查询商品列表
class GoodsSerializer(serializers.ModelSerializer):
    goodsshowimages = GoodsThirdImagesSerializer(source='goods.goodsthirdimages_set', many=True, read_only=True)
    goodsdetailimages = GoodsThirdDetailImagesSerializer(source='goods.goodsthirddetailimages_set',
                                                         many=True, read_only=True)

    class Meta:
        model = GoodsSpecs
        fields = '__all__'


# 查询商品详情
class GoodsDetailSerializer(serializers.ModelSerializer):
    goodsshowimages = GoodsThirdImagesSerializer(source='goods.goodsthirdimages_set', many=True, read_only=True)
    goodsdetailimages = GoodsThirdDetailImagesSerializer(source='goods.goodsthirddetailimages_set',
                                                         many=True, read_only=True)
    discountgoods_set = DiscountGoodsSerializer(many=True, read_only=True)

    class Meta:
        model = GoodsSpecs
        fields = ['id', 'goods_specs', 'goods_title', 'goods_price', 'goods_introduction', 'goods_sale',
                  'goodsshowimages', 'goodsdetailimages', 'discountgoods_set']
        # fields = '__all__'


class ComposedGoodsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComposedGoodsImages
        fields = ['img_composed']


class ComposedGoodsSerializer(serializers.ModelSerializer):
    composedgoodsimages_set = ComposedGoodsImagesSerializer(many=True,read_only=True)

    class Meta:
        model = ComposedGoods
        fields = ['id', 'composedgoodsimages_set', 'composed_goods_name', 'composed_goods_detail',
                  'composed_goods_description', 'old_price', 'new_price']


# 查询组合商品详情
class ComposedGoodsDetailSerializer(serializers.ModelSerializer):
    composedgoodsimages_set = ComposedGoodsImagesSerializer(many=True, read_only=True)

    class Meta:
        model = ComposedGoods
        fields = ['id', 'composedgoodsimages_set', 'composed_goods_name', 'composed_goods_detail',
                  'composed_goods_description', 'old_price', 'new_price']


# 创建订单商品
class OrderCreatSerialzer(serializers.ModelSerializer):
    shop_cart_ids = serializers.CharField(label='购物车id', write_only=True)

    # goods_quantity = serializers.IntegerField(label='购物车商品数量', read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['id', 'shop_cart_ids']

    def generate_order_number(self):
        random_num = Random()
        order_number = '{time}{number}'.format(time=strftime('%Y%m%d%H%M%S'), number=random_num.randint(10, 99))

        return order_number

    def validate(self, attrs):
        attrs['order_number'] = self.generate_order_number()
        return attrs

    def validate_shop_cart_ids(self, value):
        try:
            ids = value.split('-')
        except:
            raise serializers.ValidationError('输入格式错误！', code='code_error')
        return ids

    def create(self, validated_data):
        carts_shop = Cart.objects.filter(Q(user_id=self.context['request'].user.id) & Q(id__in=validated_data['shop_cart_ids']))
        validated_data.pop('shop_cart_ids')
        if carts_shop:
            validated_data['sum_goods'] = 0
            validated_data['sum_price'] = 0
            validated_data['user_id'] = self.context['request'].user.id

            order = OrderInfo.objects.create(**validated_data)
            for cart_shop in carts_shop:
                order_goods = OrderGoods()

                order_goods.goods = cart_shop.goods
                order_goods.goods_quantity = cart_shop.goods_number
                order_goods.user_id = self.context['request'].user.id
                order_goods.order = order
                order_goods.save()
                cart_shop.delete()
            order.save()
            return order


# 查看订单商品
class OrderGoodsSerializer(serializers.ModelSerializer):
    goods_details = GoodsSpecsSerialzer(many=False, read_only=True)

    class Meta:
        model = OrderGoods
        fields = ['goods_details', 'user', 'goods_quantity', 'order']

class OrderInfoListSerializer(serializers.ModelSerializer):
    order_goods = OrderGoodsSerializer(source='ordergoods_set',many=True,read_only=True)
    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    goods = GoodsSpecsSerialzer(many=False, read_only=True)
    # goods = serializers.CharField(source='goods.goods_title',read_only=True)
    user_name = serializers.CharField(source='user.username',read_only=True)
    goods_image = GoodsThirdImagesSerializer(source='goods.goodsthirdimages_set', many=True, read_only=True)

    # user_name = SerializerMethodField()
    order_num = serializers.CharField(source='order.order_number',read_only=True)
    # goods_price = serializers.CharField(source='goods.goods_price',read_only=True)
    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderInfoDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = '__all__'

# 搜索
class SearchSerialzer(serializers.ModelSerializer):
    # goods_details = GoodsThirdClassSerialzer(many=False, read_only=True)

    class Meta:
        model = GoodsSpecs
        fields = '__all__'