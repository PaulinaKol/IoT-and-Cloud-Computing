# Generated by Django 5.2.2 on 2025-06-25 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_userprofile_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicenotification',
            name='msg_type',
            field=models.CharField(choices=[('MAIL_IN', 'Przesyłka włożona'), ('MAIL_OUT', 'Przesyłka wyjęta'), ('LOW_BATTERY', 'Niski poziom baterii'), ('CONNECTION_LOST', 'Utrata połączenia')], max_length=20),
        ),
    ]
