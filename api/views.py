import datetime
import jwt
import rest_framework.exceptions
from . import serializers
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from api.models import User, Material
from .ml import get_info_from_user, get_stat_picture

GLOBAL_ADRESSES = None

def welcome(request):
	return HttpResponse("<h1>Welcome</h1>")


class RegisterView(APIView):
	def post(self, request) -> Response:
		serializer = serializers.UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)


class LoginView(APIView):
	def post(self, request) -> Response:
		if not request.data.get("username") or not request.data.get("password"):
			raise AuthenticationFailed({
				"username": "username",
				"password": "password"
			})
		
		username = request.data["username"]
		password = request.data["password"]
		
		user = User.objects.filter(username=username).first()
		
		if user is None:
			raise AuthenticationFailed("User not found!")
		
		if not user.check_password(password):
			raise AuthenticationFailed("Incorrect password!")
		payload = {
			"id": user.id,
			"exp": datetime.datetime.utcnow() + datetime.timedelta(days=60),
			"iat": datetime.datetime.utcnow()
		}
		
		token = jwt.encode(payload, "secret", algorithm="HS256")
		
		response = Response()
		
		response.set_cookie(key="jwt", value=token, httponly=True)
		response.data = {
			"jwt": token
		}
		return response


class LogoutView(APIView):
	def post(self, request):
		response = Response()
		
		response.delete_cookie("jwt")
		response.data = {
			"message": "success"
		}
		return response


class UserGetView(APIView):
	def get(self, request):
		
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("id"):
			return Response(
				{"id": "required"}
			)
		
		user = User.objects.get(id=request.data["id"])
		serializer = serializers.UserSerializer(user)
		return Response(serializer.data)

class SubscribeView(APIView):
	
	def post(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("id"):
			return Response(
				{"id": "required"}
			)
		
		catched_user = User.objects.get(id=request.data["id"])
		catched_user_podpischiki = catched_user._get_subscribers
		
		logged_user = User.objects.get(id=payload['id'])
		logged_user_podpiski = logged_user._get_subscription
		
		
		if catched_user in logged_user_podpiski or logged_user in catched_user_podpischiki:
			return Response({"status": "bad", "message": "Already subscribed"})
		
		catched_user.subscribers += "{} ".format(payload['id'])
		logged_user.subscription += "{} ".format(request.data["id"])
		catched_user.save()
		logged_user.save()

		return Response({"status": "ok", "message": "Subscribed"})

class SubscribersListView(APIView):
	
	def get(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("id"):
			return Response(
				{"id": "required"}
			)
		
		user = User.objects.get(id=request.data["id"])
		subscribers_list_ser = serializers.UserSerializer(user._get_subscribers, many=True)
		serializer = serializers.UserSerializer(user)

		return Response(subscribers_list_ser.data)


class SubscriptionListView(APIView):
	
	def get(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("id"):
			return Response(
				{"id": "required"}
			)
		
		user = User.objects.get(id=request.data["id"])
		subscribers_list_ser = serializers.UserSerializer(user._get_subscription, many=True)
		serializer = serializers.UserSerializer(user)
		
		return Response(subscribers_list_ser.data)


class GetFromUserMaterialsView(APIView):
	def get(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("user_id"):
			return Response(
				{"user_id": "required"}
			)
		
		catched_user = User.objects.get(id = request.data["user_id"])
		user_materials = catched_user.material_set.order_by('-id')
		
		serializer = serializers.MaterialSerializer(user_materials, many=True)
		return Response(serializer.data)


class CreateMaterialView(APIView):
	def post(self, request):
		
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		request.data._mutable = True
		request.data.setdefault("author", payload["id"])
		
		serializer = serializers.MaterialSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)


class LentaSubscriptionView(APIView):
	
	def get(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		logged_user = User.objects.get(id=payload["id"])
		subscription_list_with_user_objects = []
		for u in logged_user._get_subscription:
			user_materials = u.material_set.order_by('-id')
			
			subscription_list_with_user_objects.append(
				serializers.MaterialSerializer(user_materials, many=True).data
			)
		
		if not subscription_list_with_user_objects:
			return Response([])
		
		return Response(subscription_list_with_user_objects[0])


class SetLikeMaterialView(APIView):
	def post(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("material_id"):
			return Response(
				{"material_id": "required"}
			)
		
		m = Material.objects.get(id=request.data['material_id'])
		m.likes_count += 1
		m.save()
		
		return Response({"status": "ok", "message": "liked"})


class MaterialCommentList(APIView):
	def get(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("material_id"):
			return Response(
				{"material_id": "required"}
			)
		
		m = Material.objects.get(id=request.data['material_id'])
		comments = m.materialcomment_set.order_by('-id')
		serializer = serializers.MaterialCommentSerializer(comments, many=True)
		return Response(serializer.data)


class LeaveMaterialCommentView(APIView):
	def post(self, request):
		token = request.COOKIES.get("jwt")
		
		if not token:
			raise AuthenticationFailed("Unauthenticated!")
		
		try:
			payload = jwt.decode(token, "secret", algorithms=["HS256"])
		except jwt.ExpiredSignatureError:
			raise AuthenticationFailed("Unauthenticated!")
		
		if not request.data.get("material_id"):
			return Response({"material_id": "required"})
		
		request.data._mutable = True
		request.data.setdefault("comment_author", payload["id"])
		request.data.setdefault("material", request.data["material_id"])  # TODO: index out of the range!
		
		serializer = serializers.MaterialCommentSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)


class MLGetInfoFromUser(APIView):
	def post(self, request):
		serializer = serializers.MLGetInfoFromUser(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		global GLOBAL_ADRESSES

		result, GLOBAL_ADRESSES = get_info_from_user(
			serializer.data["user_gtin"],
			serializer.data["user_region_code"],
			serializer.data["user_n_classes"],
		)

		print("\n\n\n\n\n")
		print("mlgetinfo", GLOBAL_ADRESSES)
		print("\n\n\n\n\n")

		return Response({"result": result})


class MLGetStatPicture(APIView):
	def post(self, request):
		serializer = serializers.MLGetStatPictureFromUser(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		global GLOBAL_ADRESSES

		print("\n\n\n\n\n")
		print(GLOBAL_ADRESSES)
		print("\n\n\n\n\n")

		result = get_stat_picture(
			serializer.data["user_number_of_cluster"],
			serializer.data["user_product_name"],
			GLOBAL_ADRESSES,
		)

		return Response({"result": True})
