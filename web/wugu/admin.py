from django.contrib import admin

# Register your models here.
from wugu.models import UserInfo, OrderInfo, UserPreference, ReceiveInfo, GoodsImages, GoodsSpecs, \
    ComposedGoods, Tips, IndexCarousel, \
    DiscountGoods, OrderAddress, Comment, OrderGoods, Cart, GoodsCollection, GoodsFirst, GoodsSecond, GoodsThird, \
    Carriage, GoodsThirdImages, GoodsThirdDetailImages, ComposedGoodsImages

admin.site.site_title = '食间杂货店'
admin.site.site_header = '食间杂货店'

# 用户信息
@admin.register(UserInfo)
class AuthorAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'username', 'phone',  'email', 'user_img')
    list_display_links = ('id', 'username', 'phone',  'email', 'user_img')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('gender',)  # 过滤器
    search_fields = ('username', 'gender', 'is_admin')  # 搜索字段


# 用户偏好
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('preference',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'preference')
    list_display_links = ('id', 'preference')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('user',)  # 搜索字段


# 收件信息
@admin.register(ReceiveInfo)
class ReceiveInfoAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'user', 'receiver', 'address',  'telephone')
    list_display_links = ('id', 'user', 'receiver', 'address', 'telephone')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'user', 'receiver', 'telephone')  # 搜索字段


# 商品图片
@admin.register(GoodsImages)
class GoodsImagesAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_img')
    list_display_links = ()     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ()  # 搜索字段


# 商品一类
@admin.register(GoodsFirst)
class GoodsFirstAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_first_class')
    list_display_links = ('id', 'goods_first_class')     # 设置哪些字段可以点击进入编辑界面

    # list_filter = ('goods_specs', 'goods_price')  # 过滤器
    search_fields = ('id', 'goods_first_class')  # 搜索字段


# 商品二类
@admin.register(GoodsSecond)
class GoodsSecondAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_second_class', 'goods_first_class')
    list_display_links = ('id', 'goods_second_class', 'goods_first_class')     # 设置哪些字段可以点击进入编辑界面

    # list_filter = ('goods_specs', 'goods_price')  # 过滤器
    search_fields = ('id', 'goods_second_class')  # 搜索字段


# 商品三类
@admin.register(GoodsThird)
class GoodsThirdAdmin(admin.ModelAdmin):
    list_per_page = 30      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_name', 'goods_detail')
    list_display_links = ('id', 'goods_name', 'goods_detail')    # 设置哪些字段可以点击进入编辑界面

    # list_filter = ('goods_specs', 'goods_price')  # 过滤器
    search_fields = ('id', 'goods_name')  # 搜索字段


# 商品规格
@admin.register(GoodsSpecs)
class GoodsSpecsAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('-id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_specs', 'goods_title', 'goods_price')
    list_display_links = ('id', 'goods_specs', 'goods_title', 'goods_price')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'goods_specs', 'goods_price')  # 搜索字段


# 组合商品
@admin.register(ComposedGoods)
class ComposedGoodsAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'composed_goods_name', 'composed_goods_description', 'composed_goods_detail',
                    'old_price', 'new_price')
    list_display_links = ('id', 'composed_goods_name', 'composed_goods_description', 'old_price',
                          'new_price')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'composed_goods_name')  # 搜索字段


# 组合商品图
@admin.register(ComposedGoodsImages)
class ComposedGoodsImagesAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'img_composed', 'composed_goods')
    list_display_links = ('id', 'img_composed', 'composed_goods')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'composed_goods')  # 搜索字段


# 五谷小知识
@admin.register(Tips)
class TipsAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'tips_text', 'tips_img')
    list_display_links = ('id', 'tips_text')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'tips_text')  # 搜索字段


# 首页图片轮播
@admin.register(IndexCarousel)
class IndexCarouselAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'number', 'image')
    list_display_links = ('id', 'number', 'image')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'number')  # 搜索字段


# 打折商品
@admin.register(DiscountGoods)
class DiscountGoodsAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods', 'discounted_price')
    list_display_links = ('id', 'goods', 'discounted_price')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'goods')  # 搜索字段


# 订单地址
@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'user', 'addressee', 'addressee_phone', 'address', 'is_default')
    list_display_links = ('id', 'user', 'addressee', 'addressee_phone', 'address', 'is_default')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'user', 'is_default')  # 搜索字段


# 订单信息
@admin.register(OrderInfo)
class OrderInfoAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'user', 'order_number', 'express', 'sum_goods', 'sum_price',
                    'payment_status', 'order_generation_time')
    list_display_links = ('id', 'order_number', 'express', 'payment_status')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('pay_ways', 'express', 'payment_status')  # 过滤器
    search_fields = ('id', 'user', 'order_number', 'express', 'express', 'payment_status')  # 搜索字段


# 评论
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'goods_specs', 'star', 'comment_detail', 'comment_time')
    list_display_links = ('id', 'goods_specs', 'star')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('star',)  # 过滤器
    search_fields = ('id', 'goods_specs', 'star', 'comment_time')  # 搜索字段


# 订单商品
@admin.register(OrderGoods)
class OrderGoodsAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'order', 'goods', 'goods_quantity')
    list_display_links = ('order', 'goods')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('id', 'order', 'goods')  # 过滤器
    search_fields = ('id', 'order', 'goods')  # 搜索字段


# 购物车
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序

    list_display = ('id', 'user', 'goods', 'goods_number', 'cart_generation_time')
    list_display_links = ('id', 'user', 'goods')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'user', 'goods')  # 搜索字段


# 收藏
@admin.register(GoodsCollection)
class GoodsCollectionAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序
    list_display = ('id', 'user', 'goods', 'is_collected')
    list_display_links = ('id', 'user', 'goods', 'is_collected')  # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'user', 'goods', 'is_collected')  # 搜索字段


# 运费
@admin.register(Carriage)
class CarriageAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    # ordering = ('-last_login',)     # ordering设置默认排序字段，负号表示降序排序
    list_display = ('id', 'express', 'carriage')
    list_display_links = ('id', 'express', 'carriage')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ('express',)  # 过滤器
    search_fields = ('id', 'express',)  # 搜索字段


# # 商品详情图
# @admin.register(GoodsDetailImages)
# class GoodsDetailImagesAdmin(admin.ModelAdmin):
#     list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
#     ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序
#     list_display = ('id', 'img_s1', 'img_b1', 'img_s2', 'img_b2', 'img_s3', 'img_b3', 'img_s4', 'img_b4',
#                     'img_d1', 'img_d2', 'img_d3' )
#     list_display_links = ('id',)     # 设置哪些字段可以点击进入编辑界面
#
#     list_filter = ()  # 过滤器
#     search_fields = ('id',)  # 搜索字段


# 商品三类展示图
@admin.register(GoodsThirdImages)
class GoodsThirdImagesAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('-id',)     # ordering设置默认排序字段，负号表示降序排序
    list_display = ('id', 'img_show', 'img_detail', 'goods')
    list_display_links = ('id', 'img_show', 'img_detail', 'goods')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'goods')  # 搜索字段

# 商品三类详情图
@admin.register(GoodsThirdDetailImages)
class GoodsThirdDetailImagesAdmin(admin.ModelAdmin):
    list_per_page = 20      # list_per_page设置每页显示多少条记录，默认是100条
    ordering = ('id',)     # ordering设置默认排序字段，负号表示降序排序
    list_display = ('id', 'img_detail', 'goods')
    list_display_links = ('id', 'img_detail', 'goods')     # 设置哪些字段可以点击进入编辑界面

    list_filter = ()  # 过滤器
    search_fields = ('id', 'goods')  # 搜索字段


