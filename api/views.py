import datetime
import jwt
import rest_framework.exceptions
from . import serializers
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from api.models import User


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
		catched_user_podpischiki = catched_user._get_subscribers()
		
		logged_user = User.objects.get(id=payload['id'])
		logged_user_podpiski = logged_user._get_subscription()
		
		
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