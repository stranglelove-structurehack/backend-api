from rest_framework import serializers
from api.models import User, Material

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'fio', 'phone', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['url_to_photo', 'url_to_open_3d_obj', 'description', 'author']

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.save()
        return instance