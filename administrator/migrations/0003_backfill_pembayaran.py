from django.db import migrations


def create_missing_payments(apps, schema_editor):
    Penyewaan = apps.get_model('administrator', 'Penyewaan')
    Pembayaran = apps.get_model('administrator', 'Pembayaran')

    for penyewaan in Penyewaan.objects.all().iterator():
        Pembayaran.objects.get_or_create(
            penyewaan_id=penyewaan.id,
            defaults={
                'jumlah': penyewaan.total_biaya,
                'metode': penyewaan.metode_pembayaran,
                'status': 'menunggu',
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ('administrator', '0002_remove_penyewaan_administrator_validator_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_payments, migrations.RunPython.noop),
    ]
