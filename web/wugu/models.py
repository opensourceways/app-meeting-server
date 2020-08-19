from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models


# Create your models here.
class MyUserManager(BaseUserManager):
    def create_superuser(self, username, password, phone, email):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.model(
            username=username,
            password=password,
            phone=phone,
            email=email
        )
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user


# 用户信息类
class UserInfo(AbstractBaseUser):
    sex_list = (
        (0, '女'),
        (1, '男'),
        (2, '保密')
    )
    username = models.CharField('登录名', max_length=20, unique=True, null=True)
    password = models.CharField('密码', max_length=128, null=True)
    gender = models.SmallIntegerField('性别', choices=sex_list, default=2, null=True)
    phone = models.CharField('电话', max_length=11, unique=True, blank=True)
    email = models.EmailField('邮箱', unique=True, null=True)
    image = models.ImageField('头像', null=True)
    is_active = models.BooleanField('账户是否激活', default=True)
    is_admin = models.BooleanField('账户是否后台管理员', default=False)
    user_img = models.ImageField('用户头像', null=True, blank=True)
    objects = MyUserManager()
    USERNAME_FIELD = 'username'  # 登录字段
    REQUIRED_FIELDS = ['password', 'phone', 'email']  # 注册必填字段

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes,
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        verbose_name_plural = '用户信息'


# 用户偏好类
class UserPreference(models.Model):
    preference = models.CharField('用户偏好', max_length=20)
    user = models.ManyToManyField(UserInfo, verbose_name='用户id')

    class Meta:
        verbose_name_plural = '用户偏好'


# 收件信息表
class ReceiveInfo(models.Model):
    receiver = models.CharField('收件人', max_length=20)
    address = models.CharField('收件地址', max_length=255)
    telephone = models.CharField('电话', max_length=11)
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '收件信息'


# 商品一类表
class GoodsFirst(models.Model):
    goods_first_class = models.CharField('商品一类', max_length=20)

    class Meta:
        verbose_name_plural = '商品一类'


# 商品三类表
class GoodsThird(models.Model):
    goods_name = models.CharField('商品名称', max_length=20, unique=True)
    goods_detail = models.CharField('商品详情', max_length=255)

    class Meta:
        verbose_name_plural = '商品三类'


# 商品二类表
class GoodsSecond(models.Model):
    goods_second_class = models.CharField('商品二类', max_length=20)
    goods_first_class = models.ForeignKey(GoodsFirst, verbose_name='商品一类', on_delete=models.SET_NULL, null=True)
    goods_third_class = models.ManyToManyField(GoodsThird, verbose_name='商品三类')

    class Meta:
        verbose_name_plural = '商品二类'


# 商品规格表
class GoodsSpecs(models.Model):
    goods_specs = models.CharField('商品规格', max_length=20)
    goods_title = models.CharField('商品标题', max_length=20, null=True)
    goods_price = models.CharField('商品价格', max_length=20)
    goods_introduction = models.CharField('商品简介', max_length=255, default='纯天然，无公害')
    goods = models.ForeignKey(GoodsThird, verbose_name='三类商品', on_delete=models.SET_NULL, null=True)
    goods_sale = models.IntegerField('商品销量', default=0)

    class Meta:
        verbose_name_plural = '商品规格'


# 商品主图表
class GoodsImages(models.Model):
    goods_img = models.ImageField('商品主图')
    goods_img_detail = models.ImageField('商品详情图', default=0)
    goods = models.ForeignKey(GoodsThird, verbose_name='三类商品', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '商品图片'


# 商品三类展示图表
class GoodsThirdImages(models.Model):
    img_show = models.ImageField('商品展示图')
    img_detail = models.ImageField('商品详情图', null=True, blank=True)
    goods = models.ForeignKey(GoodsThird, verbose_name='三类商品', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = '商三展示图'


# 商品三类详情图表
class GoodsThirdDetailImages(models.Model):
    img_detail = models.ImageField('商品详情图', null=True, blank=True)
    goods = models.ForeignKey(GoodsThird, verbose_name='三类商品', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name_plural = '商三详情图'


class GoodsDetailImages(models.Model):
    '''不用这个表了'''
    img_s1 = models.ImageField('小图1')
    img_b1 = models.ImageField('大图1')
    img_s2 = models.ImageField('小图2')
    img_b2 = models.ImageField('大图2')
    img_s3 = models.ImageField('小图3')
    img_b3 = models.ImageField('大图3')
    img_s4 = models.ImageField('小图4')
    img_b4 = models.ImageField('大图4')
    img_d1 = models.ImageField('详情图1')
    img_d2 = models.ImageField('详情图2')
    img_d3 = models.ImageField('详情图3')
    goods = models.ForeignKey(GoodsSpecs, verbose_name='商品', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '商品详情图'


# 组合商品表
class ComposedGoods(models.Model):
    composed_goods_name = models.CharField('组合商品名称', max_length=100, null=True, blank=True)
    composed_goods_detail = models.CharField('组合商品详情',max_length=255, null=True, blank=True)
    composed_goods_description = models.CharField('组合商品描述', max_length=255)
    old_price = models.CharField('原价', max_length=20, null=True, blank=True)
    new_price = models.CharField('现价', max_length=20, null=True, blank=True)

    class Meta:
        verbose_name_plural = '组合商品'


# 组合商品图
class ComposedGoodsImages(models.Model):
    img_composed = models.ImageField('组合商品图')
    composed_goods = models.ForeignKey(ComposedGoods, verbose_name='组合商品', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '组合商品图'


# 五谷小知识表
class Tips(models.Model):
    tips_text = models.TextField('五谷小知识')
    tips_img = models.ImageField('五谷小知识配图')

    class Meta:
        verbose_name_plural = '五谷小知识'


# 首页图片轮播表
class IndexCarousel(models.Model):
    image = models.ImageField('轮播图片')
    number = models.IntegerField('序号')

    class Meta:
        verbose_name_plural = '首页轮播'


# 打折商品表
class DiscountGoods(models.Model):
    discounted_price = models.DecimalField('折扣价', max_digits=8, decimal_places=2, null=True)
    goods = models.ForeignKey(GoodsSpecs, verbose_name='商品', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '打折商品'


# 订单地址表
class OrderAddress(models.Model):
    addressee = models.CharField('收件人', max_length=20)
    addressee_phone = models.CharField('收件人电话', max_length=11)
    address = models.CharField('收件地址', max_length=255)
    is_default = models.BooleanField('是否默认收货地址', default=False)
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '订单地址'


# 订单信息表
class OrderInfo(models.Model):
    pay_ways_list = (
        (1, '支付宝'),
        (2, '微信'),
        (3, '银联')
    )
    express_list = (
        (1, '普通快递(包邮)'),
        (2, '顺丰'),
        (3, 'EMS')
    )
    payment_status_list = (
        (0, '待支付'),
        (1, '已支付'),
        (2, '退款中'),
        (3, '已退款')
    )
    order_number = models.BigIntegerField('订单编号')  # 位数不够则改为BigIntegerField
    pay_ways = models.SmallIntegerField('支付方式', choices=pay_ways_list, default=1)
    carriage = models.DecimalField('运费', max_digits=4, decimal_places=2, null=True, blank=True)
    express = models.SmallIntegerField('快递方式', choices=express_list, default=1)
    sum_goods = models.IntegerField('商品总数', null=True, blank=True)
    sum_price = models.DecimalField('商品总价', max_digits=8, decimal_places=2, null=True, blank=True)
    payment_status = models.SmallIntegerField('支付状态', choices=payment_status_list, default=1)
    order_generation_time = models.DateTimeField('订单生成时间', auto_now_add=True)
    address = models.ForeignKey(OrderAddress, verbose_name='地址', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '订单信息'


# 订单商品表
class OrderGoods(models.Model):
    order = models.ForeignKey(OrderInfo, verbose_name='订单', on_delete=models.SET_NULL, null=True)
    goods = models.ForeignKey(GoodsSpecs, verbose_name='商品', on_delete=models.SET_NULL, null=True)
    goods_quantity = models.IntegerField('商品数量')
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '订单商品'


# 邮费表
class Carriage(models.Model):
    express_list = (
        (1, '普通快递(包邮)'),
        (2, '顺丰'),
        (3, 'EMS')
    )
    express = models.SmallIntegerField('快递方式', choices=express_list, default=1)
    carriage = models.DecimalField('运费', max_digits=4, decimal_places=2)

    class Meta:
        verbose_name_plural = '邮费'


# 评价表
class Comment(models.Model):
    star_list = (
        (1, '非常不满意'),
        (2, '不满意'),
        (3, '一般'),
        (4, '满意'),
        (5, '非常满意')
    )
    comment_detail = models.CharField('详细评价', max_length=255)
    star = models.SmallIntegerField('星级', choices=star_list)
    goods_specs = models.ForeignKey(GoodsSpecs, verbose_name='规格',  on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)
    comment_time = models.DateTimeField('评价时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = '评价'


# 购物车表
class Cart(models.Model):
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)
    goods = models.ForeignKey(GoodsSpecs, verbose_name='商品', on_delete=models.SET_NULL, null=True)
    goods_number = models.IntegerField('商品数量')
    cart_generation_time = models.DateTimeField('购物车创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = '购物车'


# 收藏表
class GoodsCollection(models.Model):
    is_collected = models.BooleanField('是否收藏', default=False)
    user = models.ForeignKey(UserInfo, verbose_name='用户', on_delete=models.SET_NULL, null=True)
    goods = models.ForeignKey(GoodsSpecs, verbose_name='商品', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = '收藏'
