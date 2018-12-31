from django import forms
from .models import ShoppingUser
from django.utils.translation import ugettext_lazy as _


class UserSignupForm(forms.ModelForm):
    username = forms.RegexField(regex=r'^\w+$',
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'required': 'True',
                                                              'max_length': 30,
                                                              'placeholder': 'نام کاربری',
                                                              'style': 'text-align:left'}
                                                       ),
                                label=_("نام کاربری"),
                                error_messages={
                                    'invalid': _("تنها استفاده از حروف انگلیسی، اعداد و _ در نام کاربری مجاز است."),
                                    'required': _('لطفا نام کاربری را وارد کنید')})
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': 'True',
                                                                  'max_length': 30,
                                                                  'render_value': 'False',
                                                                  'placeholder': 'رمز عبور',
                                                                  'style': 'text-align:left'}
                                                           ),
                                label=_("رمز عبور"),
                                error_messages={
                                    'required': _('لطفا رمزعبور را وارد کنید')
                                })
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control',
                                                                  'required': 'True',
                                                                  'max_length': 30,
                                                                  'render_value': 'False',
                                                                  'placeholder': 'تکرار رمز عبور',
                                                                  'style': 'text-align:left'}
                                                           ),
                                label=_("تکرار رمز عبور"),
                                error_messages={
                                    'required': _('لطفا رمزعبور را تکرار کنید')
                                })

    class Meta:
        model = ShoppingUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'province', 'city']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control',
                                                 'placeholder': 'نام',
                                                 'style': 'text-align:right',
                                                 'direction': 'rtl'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control',
                                                'placeholder': 'نام خانوادگی',
                                                'style': 'text-align:right',
                                                'direction': 'rtl'}),
            'email': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'ایمیل',
                                            'style': 'text-align:left'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control',
                                                   'placeholder': 'شماره تماس',
                                                   'style': 'text-align:left'}),
            'province': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': 'استان',
                                               'style': 'text-align:right',
                                               'direction': 'rtl'}),
            'city': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'شهر',
                                           'style': 'text-align:right',
                                           'direction': 'rtl'}),
        }
        labels = {
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
            'phone_number': _('شماره تلفن'),
            'province': _('استان'),
            'city': _('شهر'),
        }
        error_messages = {
            'first_name': {
                'required': _('لطفا نام خود را وارد کنید')
            },
            'last_name': {
                'required': _('لطفا نام خانوادگی خود را وارد کنید')
            },
            'email': {
                'required': _('لطفا ایمیل خود را وارد کنید'),
                'invalid': _('ایمیل اشتباه است')
            },
            'phone_number': {
                'required': _('لطفا شماره تلفن خود را وارد کنید'),
                'invalid': _('شماره تلفن اشتباه است')
            },
            'province': {
                'required': _('لطفا استان خود را وارد کنید')
            },
            'city': {
                'required': _('لطفا شهر خود را وارد کنید')
            }
        }

    def clean(self):
        cleaned_data = super(UserSignupForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('رمزعبور یکسان نیست')
        return cleaned_data