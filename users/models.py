from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models


# Create your models here.

class TblUser(AbstractUser, PermissionsMixin):
    phone = models.CharField(max_length=12, unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'tbl_user'

    def __str__(self):
        return self.username
