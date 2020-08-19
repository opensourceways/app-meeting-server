from django.urls import path

from wugu.models import OrderGoods
from wugu.views import RegisterView, GoodsDetailView, \
    PersonalCenterView, OrderView, PayResultView, PhoneCodeView, \
    GoodsFirstListView, GoodsSecondListView, CartCutView, UserPreferenceView, IndexCarouselView, TipsView, \
    OrderAddressView, OrderAddressDetailView, CheckView, ChangeUserInfoView, AddToCartView, OrderGoodsView, \
    OrderInfoDeleteView, ComposedGoodsDetailView, ComposedGoodsView, GoodsView, GoodsGetListView

urlpatterns = [
    path('check/', CheckView.as_view()),  # 注册前验证手机验证码
    path('register/', RegisterView.as_view()),  # 注册
    path('phone_code/', PhoneCodeView.as_view({'post': 'create'})),  # 短信验证
    # path('goods_collocation/', GoodsCollocationView.as_view()),  # 杂粮优搭配
    path('goods_first_list/', GoodsFirstListView.as_view()),  # 一类商品列表
    path('goods_second_list/', GoodsSecondListView.as_view()),  # 一类商品列表
    path('goods/', GoodsView.as_view()),  # 查询商品列表
    path('goods_detail/<int:pk>/', GoodsDetailView.as_view()),  # 商品详情
    path('composed_goods/', ComposedGoodsView.as_view()),  # 查询组合商品列表
    path('composed_goods_detail/<int:pk>/', ComposedGoodsDetailView.as_view()),  # 组合商品详情
    path('personal_center/', PersonalCenterView.as_view()),  # 个人中心
    path('order/', OrderView.as_view()),  # 订单
    path('order_goods/', OrderGoodsView.as_view({'get': 'list', 'post': 'create'})),  # 生成订单
    # path('pay/', PayView.as_view()),  # 支付页面
    path('pay_result/', PayResultView.as_view()),  # 支付结果
    path('tips/', TipsView.as_view()),  # 五谷小知识页面
    # path('goods_collocation/', GoodsCollocationView.as_view()),  # 杂粮优搭配
    path('user_preference/', UserPreferenceView.as_view()),  # 用户偏好
    path('index_carousel/', IndexCarouselView.as_view()),  # 首页轮播
    path('order_address/', OrderAddressView.as_view()),  # 订单地址
    path('order_address/<int:pk>', OrderAddressDetailView.as_view()),  # 订单地址
    path('change_user_info/', ChangeUserInfoView.as_view()),  # 修改用户信息
    path('carts/', AddToCartView.as_view({'get': 'list', 'post': 'create'})),  # 查询、新增、添加1 购物车
    path('carts/<int:pk>/', CartCutView.as_view({'put': 'update', 'delete': 'destroy'})),  # 修改、删除 购物车
    path('order_info_del/<int:pk>/', OrderInfoDeleteView.as_view()),  # 删除订单
    path('search/', GoodsGetListView.as_view())  # 搜索
]