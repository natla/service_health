import pytz
from datetime import datetime, timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint


class ServiceOutageRecord(models.Model):
    """
    Class to create records of service outage data of an application.

    The objects of the class are service records, not the services
    themselves, i.e. there can be multiple records per service
    with different outage duration, start and end times.

    In the backend API a service is represented as a list of records,
    each of which is a ServiceOutageRecord object.

    Field `service_id` is not the id/pk of the object in the database,
    which is automatically created and not serializable.
    """

    service_id = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1000)
    duration = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    start_time = models.DateTimeField(default=datetime.now())
    end_time = models.DateTimeField(null=True)

    def __init__(self, *args, **kwargs):
        """
        Calculate end_time based on start_time and duration.

        This is necessary for adding new services to the API through the
        frontend UI, since only start_time and duration get provided in the form.
        """
        super().__init__(*args, **kwargs)

        # Take the local timezone into account when calculating datetimes
        self.local_tz = pytz.timezone(settings.TIME_ZONE)

        self.end_time = self.start_time + timedelta(minutes=self.duration)

    class Meta:
        """Make sure that no duplicate service records get added to the database"""
        constraints = [
            UniqueConstraint(fields=['service_id', 'duration', 'start_time'], name='unique_service_record')]

    @property
    def healthy_service(self):
        """
        Return True if a service is healthy, i.e. it is currently up
        and has not been recently down.
        """
        return not self.service_currently_down and not self.service_recently_down

    @property
    def service_currently_down(self):
        """Return True if a service is currently down"""

        # Use local timezone for datetime.now()
        if self.end_time:
            return self.start_time <= self.local_tz.localize(datetime.now()) <= self.end_time

    @property
    def service_recently_down(self):
        """Return True if a service outage has started at some point in the last 3 hours"""

        outage_history_start = self.local_tz.localize(datetime.now()) - timedelta(hours=3)

        # Use local timezone for datetime.now()
        return outage_history_start <= self.start_time <= self.local_tz.localize(datetime.now())
