from django.db import models
from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, role=User.Types.ADMIN, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class User(AbstractUser):
    class Types(models.TextChoices):
        ADMIN = ('ADMIN', 'ADMIN')
        AGENT = ('AGENT', 'AGENT')
        SUPER_AGENT = ('SUPER_AGENT', 'SUPER_AGENT')
        DEVELOPER = ('DEVELOPER', 'DEVELOPER')

    email = models.EmailField(_('email address'), blank=False, null=False, unique=True)
    role = models.CharField(max_length=20, choices=Types.choices)
    cin = models.CharField(max_length=8, blank=False, null=False, unique=True)
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=True,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    image = models.ImageField(blank=True, null=True, upload_to='images')

    objects = UserManager()

    def save(self, *args, **kwargs):
        if self.role == User.Types.ADMIN:
            self.is_superuser = True
        else:
            self.is_superuser = False
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'users'
        permissions = [
            ("view_help", "Can view help pages"),
        ]


class Product(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    stock = models.IntegerField(blank=False, null=False, default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products'


class Command(models.Model):
    class Status(models.TextChoices):
        NEW = ('NEW', 'NEW')
        CONFIRMED = ('CONFIRMED', 'CONFIRMED')
        CANCELLED = ('CANCELLED', 'CANCELLED')
        IN_TRENSIT = ('IN_TRENSIT', 'IN_TRENSIT')
        DELIVERED = ('DELIVERED', 'DELIVERED')
        RETURNED = ('RETURNED', 'RETURNED')

    date = models.DateTimeField(null=False, blank=True, default=timezone.now)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=False)
    client_name = models.CharField(max_length=50, blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    phone_number = models.CharField(max_length=20, blank=False, null=False)
    price = models.DecimalField(max_digits=25, decimal_places=2)
    quantity = models.IntegerField(default=1, blank=False, null=False, validators=[MinValueValidator(1)])
    agent_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="agent_ids")
    agent_confirmed = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="confirmations")
    status =  models.CharField(max_length=20, choices=Status.choices)
    special_instructions = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.client_name

    class Meta:
        db_table = 'commands'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class Domain(models.Model):
    demain_name = models.CharField(max_length=50, blank=False, null=False)

    def __str__(self):
        return self.demain_name

    class Meta:
        db_table = 'domains'
