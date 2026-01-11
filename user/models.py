from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.db import models


class MyUserManager(BaseUserManager):
    # Добавляем **extra_fields, чтобы принимать любые дополнительные аргументы
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        # Передаем extra_fields при создании модели
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        # Принудительно ставим флаги админа
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(username, email, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(**{self.model.USERNAME_FIELD: email})


class MyUser(AbstractBaseUser):
    username = models.CharField(max_length=100,)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    registered_at = models.DateTimeField(auto_now_add=True)

    user_otp = models.CharField(max_length=6, null=True, blank=True)
    user_otp_created_at = models.DateTimeField(blank=True, null=True)


    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_2fa_enabled = models.BooleanField(default=False)

    objects = MyUserManager() 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class TemporaryUser(models.Model):
    username = models.CharField(max_length=100,)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    registered_at = models.DateTimeField(auto_now_add=True)