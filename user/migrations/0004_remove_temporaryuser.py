from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_seed_access_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TemporaryUser',
        ),
    ]
