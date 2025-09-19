from django import forms

from apps.authentication.models import CustomUser


class EditProfileForm(forms.ModelForm):
    # email = forms.
    class Meta:
        model = CustomUser
        fields = ('email', 'phone', 'website', 'fullname', 'address', 'zipcode', 'bio')
