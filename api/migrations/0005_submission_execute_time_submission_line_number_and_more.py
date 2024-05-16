# Generated by Django 4.2.11 on 2024-05-16 04:53

import api.model.submission
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_remove_submission_score_submission_fitness_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='execute_time',
            field=models.DurationField(null=True, verbose_name='執行時間'),
        ),
        migrations.AddField(
            model_name='submission',
            name='line_number',
            field=models.IntegerField(default=0, verbose_name='行數'),
        ),
        migrations.AddField(
            model_name='submission',
            name='score',
            field=models.IntegerField(default=0, validators=[api.model.submission.Submission.validate_range], verbose_name='分數'),
        ),
        migrations.AlterField(
            model_name='submission',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='時間'),
        ),
    ]
