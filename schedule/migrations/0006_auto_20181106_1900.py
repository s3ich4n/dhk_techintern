# Generated by Django 2.1.2 on 2018-11-06 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20181106_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='deleted',
            field=models.DateTimeField(blank=True, help_text='삭제된 시간', null=True),
        ),
    ]
