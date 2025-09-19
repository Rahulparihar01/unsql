from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_alter_connection_db_type'),
    ]

    operations = [
        migrations.RunSQL(
            # Drop the message_type column if it exists
            "ALTER TABLE home_message DROP COLUMN IF EXISTS message_type;",
            # No reverse SQL - we don't want to recreate the column
            None
        ),
    ]
