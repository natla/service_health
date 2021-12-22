# Service Health Monitor

App that visualizes the current outage data of hypothetical monitored services. Hence, not a service uptime but its downtime is being recorded in the database, and displayed in a table format in the UI.

Note that this application is a work in progress.

## Description

The web application visualizes the following data:

- Healthy services (id, startTime, duration, endTime). These are services that are currently running and have not been recently down. (By default, a service is considered healthy unless its outage data has been recorder in the database.)
- Currently down services (id, startTime, duration, endTime)
- Recently down services (id, startTime, duration, endTime)
- Flapping scenarios, which are outages where one service has been down for at least 15 minutes cumulatively in a 2-hour timeframe (id, startTime, duration, endTime, amountOfOutages, sumOfOutages)
(There are currently unit tests only for the flapping scenarios.)

- A new outage record for a service can be added through an API endpoint (directly from the API or using a form in the UI)
- All information is sortable/filterable in the frontend UI
- There is a search bar which searches in all columns
- If something fails on the backend, the UI lets the user know that there is a problem and what that problem is.

The backend is written in Python and Django (using [Django REST framework](https://www.django-rest-framework.org/))

The frontend is written in HTML/CSS/JS (used libraries: jQuery, Bootstrap)

## Live app version (frontend UI)
https://services-health-monitor.herokuapp.com/

## API endpoints
### List of all available services and their outage data:
https://services-health-monitor.herokuapp.com/api/v1/services/

Get all services from the database or post a new service record.
To bulk-create new services, provide a list of dictionaries.

### Detailed view of a single service:
https://services-health-monitor.herokuapp.com/api/v1/services/<service_id>/

Allows to get a list of records for a specific service with id=service_id, post a new record, or delete the service record.

## FIXMEs / Improvement TODOs

- Class `ServiceRecordsDetailView`: Implement method put() to make it possible to update existing services.
- Reimplement the frontend using React.js.
- UX Improvement: Add a calendar/clock widget to make it possible for the user to select service start times  (currently it is necessary to enter a specific datetime format as a text in order to add a new record).
- Add header / footer to the frontend page
- On auto refresh, reload only the service data in the table instead of the entire page
- Rework the templates to minimize hardcoding
- Filtering modal: Implement functionality for resetting and clearing the filters
(currently the way to clear the filters is to reload the homepage URL)
- Add custom HTTP error pages
