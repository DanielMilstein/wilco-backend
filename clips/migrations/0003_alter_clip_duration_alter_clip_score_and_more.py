# Generated by Django 5.1 on 2024-08-22 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clips', '0002_rename_entities_clip_speaker_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clip',
            name='duration',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='clip',
            name='score',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='clip',
            name='time_end',
            field=models.DateTimeField(null=True),
        ),
    ]
