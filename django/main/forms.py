from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import forms
from .models import Command, Product
from django.utils.html import mark_safe


order_status_changes = {
    'NEW': ['CONFIRMED', 'CANCELLED', 'IN_TRENSIT', 'DELIVERED', 'RETURNED'],
    'CONFIRMED': ['IN_TRENSIT', 'DELIVERED', 'RETURNED'],
    'CANCELLED': [],
    'IN_TRENSIT': ['DELIVERED', 'RETURNED'],
    'DELIVERED': [],
    'RETURNED': [],
}


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')


class CommandCreationForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['NEW_ORDER'] = True
        cleaned_data['QUANTITY_AMOUNT'] = 0
        # self.instance
            # check that we did not change the quantity
            # check the constrains of the status
            # if returned or cancelled update the stock of the product
        if self.instance.id:
            cleaned_data['NEW_ORDER'] = False
            if (self.instance.quantity != cleaned_data.get('quantity', None)) and (cleaned_data.get('quantity', None) is not None):
                # the quantity has been updated
                # get the added amount
                diff_amount = cleaned_data.get('quantity') - self.instance.quantity
                # check if it is available in the stock
                # false: show error message
                if diff_amount > cleaned_data['product'].stock:
                    raise ValidationError(mark_safe(f"insufficient quantity: you only have <strong>{cleaned_data['product'].stock}</strong> items of <strong>\"{cleaned_data['product'].name}\"</strong> in stock."))
                # true: update qunatity and save order
                else:
                    cleaned_data['QUANTITY_AMOUNT'] = diff_amount
            if self.instance.status != cleaned_data.get('status', None):
                if cleaned_data['status'] not in order_status_changes[self.instance.status]:
                   raise ValidationError(mark_safe(f"Order status cannot be changed from <strong>\"{self.instance.status}\"</strong> to <strong>\"{cleaned_data['status']}\"</strong>"))
                else:
                    if cleaned_data['status'] in ['CANCELLED', 'RETURNED']:
                        cleaned_data['QUANTITY_AMOUNT'] = -self.instance.quantity
        # not self.instance
            # check the quantity
        else:
            cleaned_data['NEW_ORDER'] = True
            if cleaned_data['quantity'] > cleaned_data['product'].stock:
                raise ValidationError(mark_safe(f"insufficient quantity: you only have <strong>{cleaned_data['product'].stock}</strong> items of <strong>\"{cleaned_data['product'].name}\"</strong> in stock."))
            else:
                cleaned_data['QUANTITY_AMOUNT'] = cleaned_data['quantity']
        return cleaned_data

    def save(self, *args, **kwargs):
        new_command = super().save(*args, **kwargs)
        # decrement the quantity of the product in this command
        product_to_update = new_command.product
        product_to_update.stock -= self.cleaned_data['QUANTITY_AMOUNT']
        product_to_update.save()
        return new_command

    class Meta:
        model = Command
        fields = '__all__'
