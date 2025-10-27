# Generated migration for RecordMedia model updates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DataForm', '0003_alter_record_operation'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordmedia',
            name='storage_url',
            field=models.URLField(blank=True, help_text='Cloud storage URL', max_length=500),
        ),
    ]
