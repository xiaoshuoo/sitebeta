# Generated by Django 4.2.3 on 2025-06-16 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_alter_lecture_options_remove_lecture_created_by_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='lecture',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blog.category', verbose_name='Категория'),
        ),
    ]
