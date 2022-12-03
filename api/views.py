import datetime
import jwt
import rest_framework.exceptions
from . import serializers
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, ValidationError



def welcome(request):
	return HttpResponse("<h1>Welcome</h1>")

class RegisterView(APIView):
	def post(self, request) -> Response:
		serializer = serializers.UserSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(serializer.data)