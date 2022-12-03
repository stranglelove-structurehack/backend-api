from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here. Okay.


class User(AbstractUser):
	username = models.CharField("Короткая ссылка", max_length=255, unique=True)
	email = models.CharField("Email", max_length=255, unique=True)
	password = models.CharField("Пароль", max_length=255)
	fio = models.CharField("ФИО", max_length=255)
	phone = models.CharField("Номер телефона", max_length=12) # TODO: change type from str to PhoneNumber or smth idk.

	USERNAME_FIELD = 'username'

	def __str__(self):
		return str(self.username)