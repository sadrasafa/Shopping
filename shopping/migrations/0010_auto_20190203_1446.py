# Generated by Django 2.1.4 on 2019-02-03 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0009_auto_20190203_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppinguser',
            name='referral_code',
            field=models.CharField(blank=True, default='0', max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='shoppinguser',
            name='referrer_code',
            field=models.CharField(blank=True, default='0', max_length=10, null=True),
        ),
    ]
