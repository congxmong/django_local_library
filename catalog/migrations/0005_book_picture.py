# Generated by Django 2.1.1 on 2019-01-10 23:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_auto_20181129_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='picture',
            field=models.ImageField(default='default.png', upload_to=''),
        ),
    ]
