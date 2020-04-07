from django.core.management import call_command
from django.db import migrations


def load_fixture(apps, schema_editor):
    call_command('loaddata', 'outages.json', app_label='service_outages')


def unload_fixture(apps, schema_editor):
    SHM_data = apps.get_model('service_outages', 'ServiceOutageRecord')
    SHM_data.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('service_outages', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
