from django.db import migrations
import cloudinary.models

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(
                'avatar',
                blank=True,
                null=True,
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cover',
            field=cloudinary.models.CloudinaryField(
                'cover',
                blank=True,
                null=True,
                max_length=500,
            ),
        ),
    ] 