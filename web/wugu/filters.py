from django.db.models import QuerySet, Q
from django_filters import filters
from django_filters.rest_framework import FilterSet

from wugu.models import GoodsSpecs


class GoodsThirdClassFilter(FilterSet):

    class Meta:
        model = GoodsSpecs
        fields = {
            'goods_title': ['contains'],
        }
