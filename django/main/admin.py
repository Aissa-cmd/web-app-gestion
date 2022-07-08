from django.contrib import admin
from .forms import (UserCreationForm, CommandCreationForm)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext, gettext_lazy as _
from django.utils.html import mark_safe
from import_export.admin import ImportExportModelAdmin
from .models import (Product, Command, Domain, User)
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from import_export import resources
from django.utils import timezone
from . import views as help_views
from django.urls import path


class CustomAdmonSite(admin.AdminSite):
    def get_urls(self):
        custom_urls = [
            path('help/', self.admin_view(help_views.help_index)),
            path('help/dashboard/', self.admin_view(help_views.help_dashboard)),
            path('help/domains/', self.admin_view(help_views.help_domains)),
            path('help/groups/', self.admin_view(help_views.help_groups)),
            path('help/orders/', self.admin_view(help_views.help_orders)),
            path('help/products/', self.admin_view(help_views.help_products)),
            path('help/users/', self.admin_view(help_views.help_users)),
        ]
        admin_urls = super().get_urls()
        return custom_urls + admin_urls


site = CustomAdmonSite()


class ProductModelAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'stock')
    list_display_links = ('name',)
    list_per_page = 20


class UserResource(resources.ModelResource):
    def before_import_row(self, rows, **kwargs):
        value = rows['password']
        rows['password'] = make_password(value)

    def skip_row(self, instance, original):
        return True if (User.objects.filter(email=instance.email).exists() or User.objects.filter(cin=instance.cin)) else False

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'cin', 'email', 'phone_number', 'role', 'password',)


class UserModelAdmin(UserAdmin, ImportExportModelAdmin):
    # change_password_form = AdminPasswordChangeForm
    list_display = ('id','username', 'first_name', 'last_name', 'email', 'is_staff', 'role')
    list_display_links = ('username',)
    resource_class = UserResource
    list_filter = ('role', 'is_staff')
    # list_filter = []
    search_fields = ('email', 'username', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email', 'cin', 'image', 'phone_number', 'role')}),
        (_('Permissions'), {
            'fields': ('is_staff', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'cin', 'image', 'email', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('last_login', 'date_joined')
    # add_form = UserCreationForm
    list_editable = ('role',)
    list_per_page = 20 # No of records per page 
    ordering = ['email']


class CommnadResource(resources.ModelResource):
    def before_import_row(self, rows, **kwargs):
        value = rows['date']
        rows['date'] = timezone.make_aware(timezone.datetime.strptime(value, '%d/%m/%Y'))

    class Meta:
        model = Command
        fields = (
            'id',
            'date',
            'product',
            'client_name',
            'address',
            'phone_number',
            'price',
            'quantity',
            'agent_id',
            'agent_confirmed',
            'status'
        )


class CommandModelAdmin(ImportExportModelAdmin):
    list_display = ('id', 'product_name', 'client_name', 'phone_number', 'price', 'quantity', 'agent_username', 'confirmed_agent', 'status')
    list_display_links = ('product_name',)
    list_editable = ('status',)
    list_per_page = 20
    list_filter = ('status',)
    date_hierarchy = 'date'
    form = CommandCreationForm
    resource_class = CommnadResource

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'classes': ('wide',),
                'fields': ('product', 'client_name', 'address', 'phone_number', 'price', 'quantity', 'status', 'special_instructions', 'date')
            }),
        )

    def get_changelist_form(self, request, **kwargs):
        return CommandCreationForm

    def get_readonly_fields(self, request, obj):
        if request.user.role == User.Types.AGENT:
            return ('product', 'client_name', 'address', 'phone_number', 'price', 'quantity', 'agent_id')
        else:
            return []

    def save_model(self, request, obj, form, change):
        # update the agent_id
        if obj.status != Command.Status.NEW:
            obj.agent_id = request.user
        # update the agent_confirmed
        if obj.status == Command.Status.CONFIRMED:
            obj.agent_confirmed = request.user
        super().save_model(request, obj, form, change)

    def product_name(self, obj):
        try:
            return obj.product.name
        except:
            return "Product was deleted"

    def agent_username(self, obj):
        try:
            agent_id_url = reverse(f'admin:{obj.agent_id._meta.app_label}_{obj.agent_id._meta.model_name}_change', args=(obj.agent_id.id,))
            return mark_safe(f'<a href="{agent_id_url}">{obj.agent_id.username}</a>')
        except:
            return "-"

    def confirmed_agent(self, obj):
        try:
            agent_confirmed_url = reverse(f'admin:{obj.agent_confirmed._meta.app_label}_{obj.agent_confirmed._meta.model_name}_change', args=(obj.agent_confirmed.id,))
            return mark_safe(f'<a href="{agent_confirmed_url}">{obj.agent_confirmed.username}</a>')
        except:
            return "-"


class DomainResource(resources.ModelResource):
    def import_data(self, dataset, *args, **kwargs):
        return super().import_data(dataset, *args, **kwargs)

    class Meta:
        model = Domain
        fields = ('id', 'demain_name',)


class DomainModelAdmin(ImportExportModelAdmin):
    resource_class = DomainResource
    list_display = ('demain_name', 'visit_domain')
    list_per_page = 20 # No of records per page 

    def visit_domain(self, obj):
        href = obj.demain_name
        if not obj.demain_name.startswith("http"):
            href = "https://" + href 
        if not obj.demain_name.endswith("/admin"):
            href += "/admin"
        return mark_safe(f"<a href='{href}'>{obj.demain_name}</a>")


site.register(Product, ProductModelAdmin)
site.register(User, UserModelAdmin)
site.register(Command, CommandModelAdmin)
site.register(Domain, DomainModelAdmin)
site.register(Group)
