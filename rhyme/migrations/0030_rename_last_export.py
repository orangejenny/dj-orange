from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rhyme', '0029_audit_model'),
    ]

    operations = [
        migrations.RenameField(
            model_name='song',
            old_name='last_export',
            new_name='exported_at',
        ),
        migrations.RenameField(
            model_name='album',
            old_name='last_export',
            new_name='exported_at',
        ),
    ]
