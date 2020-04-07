from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from service_outages import views

urlpatterns = [
    path(
        'api/v1/services/<int:pk>/',
        views.ServiceRecordsDetailView.as_view(),
        name='api_service_outage_records'
    ),
    path(
        'api/v1/services/',
        views.ServiceRecordsListView.as_view(),
        name='api_services_list'
    ),
    path(
        '',
        views.ServiceOutageRecordView.as_view(),
        name='services_outage_data'
    )
]

# Allows to use filename extensions on URLs, e.g. api/services.json
urlpatterns = format_suffix_patterns(urlpatterns)
