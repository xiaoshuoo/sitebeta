from django.db import migrations, models
import cloudinary.models

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),  # Измените на номер последней миграции
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name='avatar'
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cover',
            field=cloudinary.models.CloudinaryField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name='cover'
            ),
        ),
    ] 