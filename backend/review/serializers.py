from rest_framework import serializers
from records.models import EmissionRecord, AuditLog


class EmissionRecordSerializer(serializers.ModelSerializer):
    source_type = serializers.CharField(
        source='source.source_type', read_only=True)
    source_file = serializers.CharField(
        source='source.file_name', read_only=True)
    reviewed_by_name = serializers.CharField(
        source='reviewed_by.username', read_only=True)

    class Meta:
        model = EmissionRecord
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(
        source='actor.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'