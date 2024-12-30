from django.db import migrations, models
import cloudinary.models

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_increase_cloudinary_fields_length'),  # Убедитесь, что это правильное имя предыдущей миграции
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cover',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ] 