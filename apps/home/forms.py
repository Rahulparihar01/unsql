# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Connection, Auth0User


class ConnectionForm(forms.ModelForm):
    users_id = forms.CharField(widget=forms.HiddenInput())
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))  # Plain-text password

    class Meta:
        model = Connection
        fields = ['users_id', 'db_name', 'username', 'host', 'port', 'db_type']
        widgets = {
            'db_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        
    def save(self, commit=True):
        # Override the save method to handle the password
        connection = super(ConnectionForm, self).save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            connection.set_password(password)

        if commit:
            connection.save()
        return connection


"""class ConnectionForm(forms.ModelForm):
    users_id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Connection
        fields = ['users_id', 'db_name', 'username', 'password', 'host', 'port']
        widgets = {
            'db_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            'host': forms.TextInput(attrs={'class': 'form-control'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
        }"""

        

"""
class ConnectionForm(forms.ModelForm):
    auth0_user_id = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Connection
        fields = ['auth0_user_id', 'db_name', 'username', 'password', 'host', 'port']
        widgets = {
            'password': forms.PasswordInput(),
        }"""