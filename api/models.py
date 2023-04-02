from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

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


class Material(models.Model):
	url_to_photo = models.CharField("Фото материала", max_length=255)
	url_to_open_3d_obj = models.CharField("Ссылка на 3d объект", max_length=255)
	description = models.CharField("Описание материала", max_length=255)
	likes_count = models.IntegerField("Количество лайков", default=0)
	author = models.ForeignKey(User, on_delete=models.CASCADE)
	
	def __str__(self):
		return f"{self.author}: {self.url_to_open_3d_obj}"


class MaterialComment(models.Model):
	material = models.ForeignKey(Material, on_delete=models.CASCADE)
	comment_text = models.CharField("Текст комментария", max_length=200)
	comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
	pub_date = models.DateTimeField("Дата создания комментария", default=datetime.datetime.today)
	
	def __str__(self):
		return f"{self.comment_author.username}: {self.post.post_title} - {self.comment_text}"


class MLInfoFromUser(models.Model):
	user_gtin = models.CharField('user_gtin', max_length=200)
	user_region_code = models.IntegerField('user_region_code')
	user_n_classes = models.IntegerField('user_n_classes')

	def __str__(self):
		return f"{self.user_gtin} - {self.user_region_code} - {self.user_n_classes}"


class MLStatPicture(models.Model):
	user_number_of_cluster = models.IntegerField('user_number_of_cluster')
	user_product_name = models.CharField('user_product_name', max_length=200)

	def __str__(self):
		return f"{self.user_number_of_cluster} - {self.user_product_name}"
