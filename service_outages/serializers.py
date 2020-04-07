from rest_framework.validators import UniqueTogetherValidator
from rest_framework import serializers
from service_outages.models import ServiceOutageRecord


class ServiceOutageRecordSerializer(serializers.ModelSerializer):
    """
    A serializer for the ServiceOutageRecord model.

    Makes it possible to add, update, delete, list
    service outage records in the API.
    """

    class Meta:
        model = ServiceOutageRecord
        fields = (
            'service_id',
            'duration',
            'start_time',
            'end_time',
            'healthy_service',
            'service_currently_down',
            'service_recently_down'
            )

        # Make sure that duplicate service records cannot be created
        validators = [
            UniqueTogetherValidator(
                queryset=ServiceOutageRecord.objects.all(),
                fields=['service_id', 'duration', 'start_time']
                )
            ]
