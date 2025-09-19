from django.db import migrations

def sync_users(apps, schema_editor):
    Auth0User = apps.get_model('home', 'Auth0User')
    CustomUser = apps.get_model('authentication', 'CustomUser')
    Chat = apps.get_model('home', 'Chat')
    Message = apps.get_model('home', 'Message')
    Connection = apps.get_model('home', 'Connection')

    # Create CustomUser for each Auth0User
    for auth0_user in Auth0User.objects.all():
        custom_user, created = CustomUser.objects.get_or_create(
            username=auth0_user.auth0_id,
            defaults={
                'email': auth0_user.email,
                'is_active': True
            }
        )
        
        # Update related models
        Chat.objects.filter(user_id=auth0_user.id).update(user=custom_user)
        Message.objects.filter(user_id=auth0_user.id).update(user=custom_user)
        Connection.objects.filter(user_id=auth0_user.id).update(user=custom_user)

class Migration(migrations.Migration):
    dependencies = [
        ('home', '0001_initial'),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(sync_users, reverse_code=migrations.RunPython.noop),
    ]
