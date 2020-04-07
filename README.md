# Service Health Monitor

App that visualizes the current outage data of monitored services

## Task Description

You receive a json with outage information, structured like this:  
`[{ id: <id>, duration: <integer indicating minutes>,  startTime: <%Y-%M-%d %H:%M:%S>}]`

Build a web application that visualizes the current health of monitored solution.

- Currently down services (id, startTime, duration, endTime)
- Recently down services (id, startTime, duration, endTime)
- Add an endpoint, which can add a new outage for a service
- Detect flapping scenarios, which are outages where one service is down an accumulated 15 minutes of downtime in a 2 hour timeframe (id, startTime, duration, endTime, amountOfOutages, sumOfOutages)
- Add tests for the flapping scenarios
- All information should be sortable/filterable
- Search bar which searches in all columns
- The frontend should have auto refresh.
- If something fails on the backend, the UI should show let the user know that there is a problem and what that problem is.
- class `ServiceRecordsDetailView`: Implement method put() to make it possible to update services.

The backend is written in Python and Django (using [Django REST framework](https://www.django-rest-framework.org/))

The frontend is written in HTML/CSS/JS (used libraries: jQuery, Bootstrap)

## FIXMEs / Improvement TODOs

- Add header / footer to the frontend page
- On auto refresh, reload only the service data in the table instead of the entire page
- Rework the templates to minimize hardcoding
- Filtering modal: Implement functionality for resetting and clearing the filters
(currently the way to clear the filters is to reload the homepage URL)
- Add custom HTTP error pages
