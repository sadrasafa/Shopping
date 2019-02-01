from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import ShoppingUser, Product, MyLocation


class UserSignupForm(forms.ModelForm):
    username = forms.RegexField(regex=r'^\w+$',
                                widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'required': 'True',
                                                              'max_length': 30,
                                                              'placeholder': 'نام کاربری',
                                                              'style': 'text-align:right',
                                                              'direction': 'rtl'}
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
                                                                  'style': 'text-align:right',
                                                                  'direction': 'rtl'}
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
                                                                  'style': 'text-align:right',
                                                                  'direction': 'rtl'}
                                                           ),
                                label=_("تکرار رمز عبور"),
                                error_messages={
                                    'required': _('لطفا رمزعبور را تکرار کنید')
                                })

    class Meta:
        model = ShoppingUser
        fields = ['first_name', 'last_name', 'email', ]
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
                                            'style': 'text-align:right',
                                            'direction': 'rtl'}),
            # 'phone_number': forms.TextInput(attrs={'class': 'form-control',
            #                                        'placeholder': 'شماره تماس',
            #                                        'style': 'text-align:left'}),
            # 'province': forms.TextInput(attrs={'class': 'form-control',
            #                                    'placeholder': 'استان',
            #                                    'style': 'text-align:right',
            #                                    'direction': 'rtl'}),
            # 'city': forms.TextInput(attrs={'class': 'form-control',
            #                                'placeholder': 'شهر',
            #                                'style': 'text-align:right',
            #                                'direction': 'rtl'}),
        }
        labels = {
            'first_name': _('نام'),
            'last_name': _('نام خانوادگی'),
            'email': _('ایمیل'),
            # 'phone_number': _('شماره تلفن'),
            # 'province': _('استان'),
            # 'city': _('شهر'),
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
            # 'phone_number': {
            #     'required': _('لطفا شماره تلفن خود را وارد کنید'),
            #     'invalid': _('شماره تلفن اشتباه است')
            # },
            # 'province': {
            #     'required': _('لطفا استان خود را وارد کنید')
            # },
            # 'city': {
            #     'required': _('لطفا شهر خود را وارد کنید')
            # }
        }

    def clean(self):
        cleaned_data = super(UserSignupForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('رمزعبور یکسان نیست')
        return cleaned_data


class AddLocationForm(forms.ModelForm):
    CITIES = (('تبریز', 'تبریز'),
              ('ارومیه', 'ارومیه'),
              ('تهران', 'تهران'),
              ('شیراز', 'شیراز'),
              ('اصفهان', 'اصفهان'),
              ('مشهد', 'مشهد'),
              ('یزد', 'یزد'),
              ('البرز', 'البرز'),
              ('کرمان', 'کرمان'),
              ('لاهیجان', 'لاهیجان'))
    city = forms.ChoiceField(widget=forms.Select, choices=CITIES, label='شهر')

    class Meta:
        model = MyLocation
        fields = ['name', 'city', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'عنوان آدرس',
                                           'style': 'text-align:right',
                                           'direction': 'rtl'}),
            # 'city': forms.Select(attrs={'class': 'form-control',
            #                             'placeholder': 'dfadlflkdfjalk',
            #                             'style': 'text-align:right',
            #                             'direction': 'rtl'}),

            # 'city': forms.ChoiceField(widget=forms.Select, choices=CHOICES)

        }
        labels = {
            'name': _('عنوان آدرس'),
            'price': _('قیمت'),
            'description': _('توضیحات'),
            'picture': _('تصویر محصول'),
            'city': _('شهر'),
            'location': _('مکان')
        }
        error_messages = {
            'name': {
                'required': _('لطفا عنوان آدرس را وارد کنید')
            },
            'price': {
                'required': _('لطفا قیمت محصول را وارد کنید'),
                'invalid': _('لطف عدد وارد کنید')
            },
            'description': {
                'required': _('لطفا توضیحات محصول را وارد کنید'),
            },
            'picture': {
                'required': _('لطفا تصویر محصول را بارگذاری کنید')
            },
            'city': {
                'required': _('لطفا شهر خود را وارد کنید')
            }
        }


class AddProductForm(forms.ModelForm):
    # CHOICES = (('Option ۲', 'Option ۱۰'), ('Option ۵', 'Option 2'),)
    # CITIES = (('تبریز', 'تبریز'),
    #           ('ارومیه', 'ارومیه'),
    #           ('تهران', 'تهران'),
    #           ('شیراز', 'شیراز'),
    #           ('اصفهان', 'اصفهان'),
    #           ('مشهد', 'مشهد'),
    #           ('یزد', 'یزد'),
    #           ('البرز', 'البرز'),
    #           ('کرمان', 'کرمان'),
    #           ('لاهیجان', 'لاهیجان'))
    # address = forms.ChoiceField(widget=forms.Select, choices=CHOICES, label='آدرس')
    # city = forms.Choice   Field(widget=forms.Select, choices=CITIES, label='شهر')

    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'picture', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'عنوان محصول',
                                           'style': 'text-align:right',
                                           'direction': 'rtl'}),
            'price': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'قیمت به ریال',
                                            'style': 'text-align:right',
                                            'direction': 'rtl'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder': 'توضیحات',
                                                 'style': 'text-align:right; height:90px',
                                                 'direction': 'rtl'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'تصویر',
                                                       'style': 'text-align:right'}),
            'category': forms.Select(choices=Product.categories, attrs={'class': 'form-control',
                                                                           'placeholder': 'دسته بنده'})

            # 'city': forms.Select(attrs={'class': 'form-control',
            #                             'placeholder': 'dfadlflkdfjalk',
            #                             'style': 'text-align:right',
            #                             'direction': 'rtl'}),

            # 'city': forms.ChoiceField(widget=forms.Select, choices=CHOICES)

        }
        labels = {
            'name': _('عنوان محصول'),
            'price': _('قیمت'),
            'description': _('توضیحات'),
            'picture': _('تصویر محصول'),
            'category': _('دسته بندی'),
            # 'city': _('شهر'),
            # 'location': _('مکان')
        }
        error_messages = {
            'name': {
                'required': _('لطفا عنوان محصول را وارد کنید')
            },
            'price': {
                'required': _('لطفا قیمت محصول را وارد کنید'),
                'invalid': _('لطف عدد وارد کنید')
            },
            'description': {
                'required': _('لطفا توضیحات محصول را وارد کنید'),
            },
            'picture': {
                'required': _('لطفا تصویر محصول را بارگذاری کنید')
            },
            'category': {
                'required': _('لطفا دسته بندی محصول را انتخاب کنید')
            }
        }


class SearchProductForm(forms.ModelForm):
    distance = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'required': 'True',
                                                             'max_length': 30,
                                                             'render_value': 'False',
                                                             'placeholder': 'حداکثر فاصله',
                                                             'style': 'text-align:right',
                                                             'direction': 'rtl'}
                                                      ),
                               label=_("حداکثر فاصله"),
                               error_messages={
                                   'required': _('لطفا حداکثر فاصله را وارد کنید')
                               })

    class Meta:
        model = Product
        fields = ['name', 'price', 'description', 'city', 'location', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'عنوان محصول',
                                           'style': 'text-align:right',
                                           'direction': 'rtl'}),
            'price': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder': 'سقف قیمت به ریال',
                                            'style': 'text-align:right',
                                            'direction': 'rtl'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder': 'توضیحات',
                                                 'style': 'text-align:right; height: 90px',
                                                 'direction': 'rtl'}),
            'city': forms.TextInput(attrs={'class': 'form-control',
                                           'placeholder': 'شهر',
                                           'style': 'text-align:right',
                                           'direction': 'rtl'}),
            'category': forms.Select(choices=Product.categories, attrs={'class': 'form-control'})
        }
        labels = {
            'name': _('عنوان محصول'),
            'price': _('سقف قیمت'),
            'description': _('توضیحات'),
            'city': _('شهر'),
            'location': _('مکان'),
            'category': _('دسته بندی')
        }
        error_messages = {
            'name': {
                'required': _('لطفا عنوان محصول را وارد کنید')
            },
            'price': {
                'required': _('لطفا سقف قیمت محصول را وارد کنید'),
                'invalid': _('لطف عدد وارد کنید')
            },
            'description': {
                'required': _('لطفا توضیحات محصول را وارد کنید'),
            },
            'city': {
                'required': _('لطفا شهر خود را وارد کنید')
            },
            'category': {
                'required': _('لطفا دسته بندی را انتخاب کنید')
            }
        }


class IncreaseCreditForm(forms.Form):
    amount = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'required': 'True',
                                                             'max_length': 30,
                                                             'render_value': 'False',
                                                             'placeholder': 'مبلغ',
                                                             'style': 'text-align:right',
                                                             'direction': 'rtl'}
                                                      ),
                               label=_("مبلغ"),
                               error_messages={
                                   'required': _('لطفا مبلغ را وارد کنید')
                               })


class UseCreditForm(forms.Form):
    use_credit = forms.BooleanField(required=False)
    # dummy = forms.CharField(initial='dummy', widget=forms.widgets.HiddenInput())