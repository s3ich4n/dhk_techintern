# Generated by Django 2.1.2 on 2018-12-04 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_auto_20181106_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_allday',
            field=models.BooleanField(default=False, help_text='하루 종일 이벤트 여부'),
        ),
        migrations.AlterField(
            model_name='event',
            name='deleted',
            field=models.DateTimeField(help_text='삭제된 시간', null=True),
        ),
    ]