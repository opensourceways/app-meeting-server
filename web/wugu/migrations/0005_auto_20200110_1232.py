# Generated by Django 2.2.5 on 2020-01-10 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wugu', '0004_auto_20200109_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_generation_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='购物车创建时间'),
        ),
    ]
