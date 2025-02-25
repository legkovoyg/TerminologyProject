from rest_framework import serializers
from refbooks.models import RefBook, RefBookElement


class RefBookSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    code = serializers.CharField()
    name = serializers.CharField()

    class Meta:
        model = RefBook
        fields = ['id', 'code', 'name']


class RefBookElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefBookElement
        fields = ['code', 'value']