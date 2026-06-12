from rest_framework import serializers

from .models import SearchProductDocument


class SearchProductDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchProductDocument
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
