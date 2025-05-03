from django.db import migrations

def insert_default_keywords(apps, schema_editor):
    PDFKeyword = apps.get_model('dashboard', 'PDFKeyword')
    data = [
        ('Leg Use (%) R', ''),
        ('Leg Use (%) L', ''),
        ('Total Touches (#)', r'(\d+\.\d+|\d+)\s+Total Touches\s*\(#\)\s+(\d+\.\d+|\d+)'),
        ('Work Rate (yd/min)', r'(\d+\.\d+|\d+)\s+Work Rate \(yd/min\)\s+(\d+\.\d+|\d+)'),
        ('Accl/Decl (#)', r'(\d+\.\d+|\d+)\s+Accl/Decl \(#\)\s+(\d+\.\d+|\d+)'),
        ('Sprint Distance (y)', r'(\d+\.\d+|\d+)\s+Sprint Distance \(y\)\s+(\d+\.\d+|\d+)'),
        ('Distance Covered (mi)', r'(\d+\.\d+|\d+)\s+Distance Covered \(mi\)\s+(\d+\.\d+|\d+)'),
        ('Total Releases (#)', r'(\d+\.\d+|\d+)\s+Total Releases \(#\)\s+(\d+\.\d+|\d+)'),
        ('Long Possessions (#)', r'(\d+\.\d+|\d+)\s+Long Possessions \(#\)\s+(\d+\.\d+|\d+)'),
        ('Short Possessions (#)', r'(\d+\.\d+|\d+)\s+Short Possessions\s*\(#\)\s+(\d+\.\d+|\d+)'),
        ('One-Touch (#)', r'(\d+\.\d+|\d+)\s+One-Touch \(#\)\s+(\d+\.\d+|\d+)'),
        ('Ball Possessions', r'(\d+\.\d+|\d+)\s+Ball Possessions\s*\(#\)\s+(\d+\.\d+|\d+)'),
    ]

    for description, pattern in data:
        PDFKeyword.objects.update_or_create(
            description=description,
            defaults={'pattern': pattern}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),  # ajuste se sua migration anterior tiver outro nome
    ]

    operations = [
        migrations.RunPython(insert_default_keywords),
    ]
