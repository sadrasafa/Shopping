# Generated by Django 2.1.4 on 2019-02-15 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shopping', '0011_auto_20190215_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Auction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_price', models.IntegerField(null=True)),
                ('end_date', models.DateTimeField(null=True)),
                ('auctioneer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping.ShoppingUser')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Bid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(null=True)),
                ('auction', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping.Auction')),
                ('bidder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='shopping.ShoppingUser')),
            ],
        ),
    ]
