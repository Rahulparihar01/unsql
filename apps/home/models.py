# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.db.models import Max
from django.conf import settings
from apps.authentication.models import CustomUser
from cryptography.fernet import Fernet
import os
import slugify
from django.db import transaction
from django.utils import timezone

# Temporary model for backward compatibility
# TODO: Remove this model after migrating all references to CustomUser
class Auth0User(models.Model):
    auth0_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    stripe_customer_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:  
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        
        # Also update or create corresponding CustomUser
        custom_user, created = CustomUser.objects.get_or_create(
            username=self.auth0_id,
            defaults={'email': self.email}
        )
        if not created and (custom_user.email != self.email or custom_user.stripe_customer_id != self.stripe_customer_id):
            custom_user.email = self.email
            custom_user.stripe_customer_id = self.stripe_customer_id
            custom_user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

class Connection(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, default='New Connection')
    host = models.CharField(max_length=255)
    port = models.CharField(max_length=10)
    username = models.CharField(max_length=100)
    password = models.BinaryField()  
    db_name = models.CharField(max_length=100)
    db_type = models.CharField(max_length=50, default='postgres')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def set_password(self, raw_password):
        from cryptography.fernet import Fernet
        from django.conf import settings
        f = Fernet(settings.ENCRYPTION_KEY.encode())
        self.password = f.encrypt(raw_password.encode())

    def get_password(self):
        from cryptography.fernet import Fernet
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)
        try:
            f = Fernet(settings.ENCRYPTION_KEY.encode())
            password_bytes = self.password

            # Handle different types returned by BinaryField
            if isinstance(self.password, str):
                # logger.warning(f"Password for connection {self.id} is a string, converting to bytes")
                password_bytes = self.password.encode()
            elif isinstance(self.password, memoryview):
                # logger.info(f"Password for connection {self.id} is memoryview, converting to bytes")
                password_bytes = bytes(self.password)
            elif not isinstance(self.password, bytes):
                # logger.error(f"Password for connection {self.id} has unexpected type: {type(self.password)}")
                raise TypeError(f"Password must be bytes, got {type(self.password)}")

            decrypted_password = f.decrypt(password_bytes).decode()
            # logger.info(f"Successfully decrypted password for connection {self.id}")
            return decrypted_password
        except Exception as e:
            logger.error(f"Error decrypting password for connection {self.id}: {str(e)}")
            raise

    def save(self, *args, **kwargs):
        from cryptography.fernet import Fernet
        from django.conf import settings
        import logging

        logger = logging.getLogger(__name__)
        if isinstance(self.password, str):
            try:
                # Check if password is already a valid Fernet token (base64)
                f = Fernet(settings.ENCRYPTION_KEY.encode())
                f.decrypt(self.password.encode())
                logger.info(f"Connection {self.id} password is already encrypted")
            except Exception:
                logger.info(f"Encrypting password for connection {self.id}")
                self.set_password(self.password)
        elif isinstance(self.password, memoryview):
            self.password = bytes(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.db_name}"

class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)
    name=models.CharField(max_length=200)
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new instance
            self.created_at = timezone.now()
        super().save(*args, **kwargs)

class Message(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    message = models.CharField(max_length=10000)
    sql = models.CharField(max_length=10000, null=True)
    head_data = models.CharField(max_length=10000, null=True)
    system_message = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    order = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        # start a transaction
        with transaction.atomic():
            if self.order == 0:  
                # Get the maximum 'order' value from the messages of this chat
                max_order = Message.objects.filter(chat=self.chat).aggregate(Max('order'))['order__max']

                if max_order is None:  
                    self.order = 1
                else:
                    self.order = max_order + 1

            super().save(*args, **kwargs)


class Blog(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=10000)
    slug = models.CharField(max_length=200)
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, title, content):
        self.title = title
        self.content = content
        self.slug = slugify(title)