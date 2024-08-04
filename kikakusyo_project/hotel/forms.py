from django import forms
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import re
from django.core.cache import cache
from .models import CartItems, UserAddresses

def validate_phone_number(value):
    pattern = r'^(\d{3}-\d{4}-\d{4}|\d{11})$'
    if not re.match(pattern, value):
        raise ValidationError('電話番号は090-1234-5678の形式、もしくは数字11桁で入力してください。')

def validate_zip_code(value):
    pattern = r'^(\d{3}-\d{4}|\d{7})$'
    if not re.match(pattern, value):
        raise ValidationError('郵便番号は123-4567の形式、もしくは数字7桁で入力してください。')
    

class CyumonInfoUpdateForm(forms.ModelForm):  
    quantity = forms.IntegerField(label='数量', min_value=1)
    id = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = CartItems
        fields = ['quantity', 'id']
        
    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        id = cleaned_data.get('id')
        cart_item = get_object_or_404(CartItems, pk=id)
        if quantity > cart_item.product.stock:
            raise ValidationError(f'残室数を超えています {cart_item.product.stock}以下にしてください')

class UserAddressesInputForm(forms.ModelForm):
    last_name = forms.CharField(label='名前(姓)', max_length=10)
    first_name = forms.CharField(label='名前(名)', max_length=10)
    zip_code = forms.CharField(label='郵便番号', max_length=8)
    address = forms.CharField(label='住所', widget=forms.TextInput(attrs={'size': '30'}))
    phone_number = forms.CharField(label='電話番号', max_length=13)
    
    class Meta:
        model = UserAddresses
        fields = ['last_name', 'first_name', 'zip_code', 'address', 'phone_number']
        labels = {
            'last_name': '名前(姓)',
            'first_name': '名前(名)',
            'zip_code': '郵便番号',
            'address': '住所',
            'phone_number': '電話番号',
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].validators.append(validate_phone_number)
        self.fields['zip_code'].validators.append(validate_zip_code)

    def save(self, commit=True):
        useraddresses = super().save(commit=False)
        useraddresses.user = self.user
        
        duplicate_address = UserAddresses.objects.filter(
            last_name=useraddresses.last_name,
            first_name=useraddresses.first_name,
            zip_code=useraddresses.zip_code,
            address=useraddresses.address,
            phone_number=useraddresses.phone_number,
            user=useraddresses.user,
        ).first()
        
        if duplicate_address:
            duplicate_address.delete()
        
        useraddresses.save()

        # try:
        #     useraddresses.validate_unique()
        #     useraddresses.save()
        # except ValidationError as e:
            




        cache.set(f'addresses_user_{self.user.id}', useraddresses)
        return useraddresses    