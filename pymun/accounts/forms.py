from typing import Type, Dict, Any
from crispy_forms import helper, layout, utils

from django import forms
from django.contrib.auth.forms import UsernameField, ReadOnlyPasswordHashField
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

from .models import User


def fieldtostring(**kwargs):
    string = '<input class="form-control" '
    for field, value in kwargs.items():
        if field == "css_class":
            string += ('class="' + value + '" ')
        if field == 'aria_describedby':
            string += ('aria-describedby="' + value + '" ')
        if field == "name":
            string += ('id="' + value + '" max_length="' + str(User._meta.get_field(value).max_length) + '" ')
        string += (field + '="' + value + '" ')
    string += ">"
    return string


def valuetolabel(name, cont):
    return '<label for="{}">{}</label>'.format(name, cont)


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges,
    from the given username and password.
    """

    error_messages = {
        'password_mismatch': _('The two password fields didn’t match.'),
    }

    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_('Password confirmation'),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_('Enter the same password as before, for verification.'),
    )

    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(),
        help_text=_('Enter your email'),
    )

    recovery_email = forms.EmailField(
        label=_('Recovery Email (Optional)'),
        required=False,
        widget=forms.EmailInput(),
        help_text=_('Enter a backup email address in case of lost password'),
    )

    FAVORITE_COLORS_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Non-Binary'),
        ('none', 'Undeclarable')
    ]

    birthday = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=('Choose Year', 'Choose Month', 'Choose Day'),
        ),
    )

    gender = forms.ChoiceField(
        label=_('Gender'),
        required=False,
        widget=forms.Select,
        choices=FAVORITE_COLORS_CHOICES,
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1',
                  'password2', 'birthday', 'gender', 'recovery_email')
        field_classes: Dict[Any, Type[UsernameField]] = dict(username=UsernameField)


class UserUpdateFormBase(forms.ModelForm):
    birthday = forms.DateField(
        widget=forms.SelectDateWidget(
            empty_label=('Choose Year', 'Choose Month', 'Choose Day'),
        ),
    )

    password = ReadOnlyPasswordHashField(
        label=_('Password'),
        help_text=_(
            """
            Raw passwords are not stored, so there is no way to see this
            \'user’s password, but you can change the password using
            <a href=\'{}\'>this form</a>. Though right now, it\'s unsupported
            """
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get('password')
        if password:
            password.help_text = password.help_text.format('../password/')
        user_permissions = self.fields.get('user_permissions')
        if user_permissions:
            user_permissions.queryset = user_permissions.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get('password')

    class Meta:
        model = User
        fields = '__all__'


class UserUpdateFormMain(UserUpdateFormBase):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'birthday',
                  'gender', 'recovery_email', 'avatar')
        field_classes = {'username': UsernameField}


class UserUpdateFormAddons(UserUpdateFormBase):
    class Meta:
        model = User
        fields = ('gender', 'workplace', 'college', 'high_school',
                  'hometown', 'nickname', 'biography')
