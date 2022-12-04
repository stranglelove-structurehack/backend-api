from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
	username = models.CharField("Короткая ссылка", max_length=255, unique=True)
	email = models.CharField("Email", max_length=255, unique=True)
	password = models.CharField("Пароль", max_length=255)
	fio = models.CharField("ФИО", max_length=255)
	phone = models.CharField("Номер телефона", max_length=12) # TODO: change type from str to PhoneNumber or smth idk.
	
	subscribers = models.CharField("Подписчики", max_length=255, default="")  # [1, 2, 3, 4, 5]
	subscription = models.CharField("Подписки", max_length=255, default="")  # [1, 2, 3, 4, 5]
	

	# TODO: Profile pics
	
	USERNAME_FIELD = 'username'

	def __str__(self):
		return str(self.username)
	
	def __get_users_from_ids(self, ids: list) -> list:
		subs = []
		for uid in ids:
			u = User.objects.get(pk=uid)
			subs.append(u)
		return subs
	
	@property
	def _get_subscribers(self) -> list:
		return self.__get_users_from_ids([int(a) for a in str(self.subscribers).split()])
	
	@property
	def _get_subscription(self) -> list:
		return self.__get_users_from_ids([int(a) for a in str(self.subscription).split()])