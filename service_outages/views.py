import pytz
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.messages.constants import DEFAULT_LEVELS
from django.contrib.messages import get_messages
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import generics, mixins, status

from service_outages.models import ServiceOutageRecord
from service_outages.forms import AddServiceRecordForm
from service_outages.serializers import ServiceOutageRecordSerializer


class ServiceRecordsListView(mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView):
    """
    Get all services from the database or post a new service record.
    To bulk-create new services, provide a list of dictionaries.

    Also, this view is used to fetch the queryset displayed on the frontend.
    """

    queryset = ServiceOutageRecord.objects.all().order_by('service_id')
    serializer_class = ServiceOutageRecordSerializer

    # Add filters to the API
    filterset_fields = {
        'service_id': ['exact'],
        'duration': ['exact', 'lte', 'gte'],
        'start_time': ['exact', 'lte', 'gte']
    }

    def get(self, request, *args, **kwargs):
        """List a queryset"""
        response = self.list(request, *args, **kwargs)
        # Warn the user if the queryset couldn't be fetched.
        if response.status_code == status.HTTP_404_NOT_FOUND:
            messages.error(request, 'Services could not be fetched from the API.')
        return response

    def post(self, request, *args, format=None, **kwargs):
        """
        After the service records are created, return the entire queryset.

        Normally the post method returns a single record, but we need
        a queryset for the ServiceOutageRecordView.

        Bulk creation of records is allowed.
        Provide a list of dictionaries with the service record data.

        If the request data provided for creating the object is invalid,
        a 400 Bad Request response will be returned.
        """
        serializer = ServiceOutageRecordSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            # Make sure that a queryset is returned
            return self.list(request, *args, **kwargs)
        response = Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Warn the user that the serializer was not valid.
            messages.error(
                request,
                'Service records could not be created in the API due to serializer errors: {}'.format(
                    serializer.errors))
        return response


class ServiceRecordsDetailView(generics.ListCreateAPIView):
    """Get a list of service records, post a new record, or delete the service record list."""

    queryset = ServiceOutageRecord.objects.all().order_by('service_id')
    serializer_class = ServiceOutageRecordSerializer

    def get_object(self, pk):
        """
        Fetch a service by service_id.

        A service can have more than one records, that's why filter() is used.
        """
        return ServiceOutageRecord.objects.filter(service_id=pk)

    def get(self, request, pk, format=None):
        """
        Get a list of service records.

        If no service records exist for that service_id, return 404 Not Found.
        """
        service = self.get_object(pk)
        if not service:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ServiceOutageRecordSerializer(service, many=True)
        return Response(serializer.data)

    def delete(self, request, pk, format=None):
        """
        Delete a service with all its records.

        If no service records exist for that service_id, return 404.
        """
        service = self.get_object(pk)
        if not service:
            return Response(status=status.HTTP_404_NOT_FOUND)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # TODO: Implement method put() to make it possible to update services


class ServiceOutageRecordView(TemplateView):
    """Client-facing view based on the Service Health Monitor API"""

    template_name = 'service_outages/services-monitor-main.html'

    local_tz = pytz.timezone(settings.TIME_ZONE)

    def dispatch(self, request, *args, **kwargs):
        """
        Render and validate the form for adding service records through the frontend.
        Implement filtering against the URL based on the API backend.
        Render the context data used in the view template.
        """

        api_list_view_instance = ServiceRecordsListView.as_view()
        queryset = api_list_view_instance(request).data

        if request.method == "POST":
            form = AddServiceRecordForm(request.POST)
            if form.is_valid():
                form.save()
                new_record_service_id = form.cleaned_data['service_id']
                messages.success(request, (
                    f"Record succesfully created! Go to <a href='api/v1/services/{new_record_service_id}'>"
                    f"api/v1/services/{new_record_service_id}</a> to check it out."
                    ))
                return HttpResponseRedirect(reverse('services_outage_data'))
        else:
            form = AddServiceRecordForm()

        return render(request, self.template_name, {
            'localized_datetime_now': self.local_tz.localize(datetime.now()),
            'all_services': queryset,
            'healthy_services': self.healthy_services(request, queryset),
            'currently_down_services': self.currently_down_services(queryset),
            'recently_down_services': self.recently_down_services(queryset),
            'flapping_services': self.flapping_scenarios(),
            'error_messages': self.get_error_messages(request),
            'success_message': self.get_success_message(request),
            'service_form': form,
            })

    def get_error_messages(self, request):
        """Return any error messages from the API"""
        messages_obj = get_messages(request)
        error_message_const = DEFAULT_LEVELS.get('ERROR')
        return [message for message in messages_obj if message.level == error_message_const]

    def get_success_message(self, request):
        """Return a list with the success message that gets returned
        on succesful service record creation."""
        messages_obj = get_messages(request)
        success_message_const = DEFAULT_LEVELS.get('SUCCESS')
        return [message for message in messages_obj if message.level == success_message_const]

    def healthy_services(self, request, queryset):
        """Return the healthy services from the API"""
        return [obj for obj in queryset if obj.get('healthy_service')]

    def currently_down_services(self, queryset):
        """Return the currently down services from the API"""
        return [obj for obj in queryset if obj.get('service_currently_down')]

    def recently_down_services(self, queryset):
        """Return the recently down services from the API"""
        return [obj for obj in queryset if obj.get('service_recently_down')]

    def flapping_scenarios(self):
        """Return a list of flapping services"""
        return [
            ServiceOutageRecord.objects.filter(
                service_id=service_id) for service_id in self.detect_flapping_scenarios()]

    def create_service_dict(self, queryset):
        """
        Given a queryset of ServiceOutageRecord objects, create a nested
        dictionary where a service is mapped to a dictionary of lists
        containing the duration, start_time and end_time values.

        We need the service data structured in dictionaries in order
        to be able to detect flapping scenarios more easily.
        """

        service_dict = {}
        for service in queryset:
            if service.service_id not in service_dict:
                service_dict[service.service_id] = {
                    'duration': [service.duration],
                    'start_time': [service.start_time],
                    'end_time': [service.end_time]
                }
            else:
                service_dict[service.service_id]['duration'].append(service.duration)
                service_dict[service.service_id]['start_time'].append(service.start_time)
                service_dict[service.service_id]['end_time'].append(service.end_time)
        return service_dict

    def detect_flapping_scenarios(self, dataset=None):
        """
        Accept an optional dictionary dataset and return a list of services that
        have been down for at least 15 minutes cumulatively in a 2-hour timeframe.
        The outages must be more than one in the 2-hour flapping interval.
        """

        flapping_results = []
        flapping_frequency = 15  # 15 minutes
        flapping_interval = 120  # 2 hours

        # Prepare the data by sorting it in a dictionary
        dataset = dataset or self.create_service_dict(ServiceOutageRecord.objects.all().order_by('start_time'))
        for service_id in dataset:

            flapping_results.extend(self.detect_flapping_per_service(
                service_id, dataset, flapping_frequency, flapping_interval))

        return flapping_results

    def detect_flapping_per_service(self, service_id, dataset, flapping_frequency, flapping_interval):
        """
        Check if a service has been down an accumulated flapping_frequency amount of time
        in the given flapping interval.

        If the sum of that service outages reaches or exceeds the flapping frequency
        within the flapping interval and the amount of outages is greater than 1,
        add the service ID to the results list.

        Return the updated results list.
        """
        sum_outages = 0
        amount_outages = 0
        results = []

        outage_duration_list = dataset[service_id]['duration']
        outage_start_time_list = dataset[service_id]['start_time']
        outage_endtime_list = dataset[service_id]['end_time']
        flapping_end_time = outage_start_time_list[0] + timedelta(minutes=flapping_interval)

        # The amount of outages must be greater than one
        if len(outage_duration_list) <= 1:
            return results

        for idx, duration in enumerate(outage_duration_list):

            # Keep track of when one outage ends and another one starts
            outage_difference = outage_start_time_list[idx] - outage_endtime_list[idx - 1] if idx - 1 != -1 else 0
            if outage_difference and outage_difference > timedelta(minutes=flapping_interval):

                # If there is more than 120-minute time difference between outages, reset the variables
                flapping_end_time = outage_start_time_list[idx] + timedelta(minutes=flapping_interval)
                sum_outages = duration
                amount_outages = 1
            else:
                sum_outages += duration
                amount_outages += 1

            if flapping_frequency <= sum_outages <= flapping_interval and amount_outages > 1 and (
                    # The current outage must end before the end of the flapping interval
                    outage_endtime_list[idx] <= flapping_end_time):
                results.append(service_id)
                break

        return results
