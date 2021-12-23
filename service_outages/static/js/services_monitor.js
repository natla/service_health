$(document).ready(function() {

    // When a navigation item is clicked, open its corresponding div and hide the rest
    $('#all-services').on('click', function() {
      activateDiv($(this));
    });

    $('#healthy').on('click', function() {
      activateDiv($(this));
    });

    $('#currently-down').on('click', function() {
      activateDiv($(this));
    });

    $('#recently-down').on('click', function() {
      activateDiv($(this));
    });

    $('#flapping').on('click', function() {
      activateDiv($(this));
    });

    function activateDiv(navItem) {
      // Add class "active" to this nav item, remove it from the currently active li
      var currentlyActiveLi = $('#main-nav').find('li.active');
      currentlyActiveLi.removeClass('active');
      navItem.addClass('active');

      // Open the corresponding div of this nav item, hide the currently visible one
      var currentlyVisibleDiv = $('#main').find('.div-visible');
      $(currentlyVisibleDiv).removeClass('div-visible');
      var divSelector = '#div-' + navItem.attr('id');
      $(divSelector).addClass('div-visible');
    }

  // Make service table searchable and sortable by all columns
  // (using Bootstrap DataTable).
  $('.service-table').DataTable();

  // Append a font awesome search icon to the search bar
  $('input[type="search"]').parent().append(
    '<i class="fa fa-search" aria-hidden="true"></i>'
  );

  // Activate the modal functionality of the form success message
  $('#successModal').modal();

  // Activate the modal functionality of the API error messages
  $('#errorsModal').modal();

  // DateTimePicker widget for the "Outage Start Datetime" input field
  // in the "Add Service Outage Record" form,
  // as well as the relevant fields in the filtering menu.
  const dateTimePicker = {
      format: 'YYYY-MM-DD HH:mm:ss',
      showClear: true,
      showClose: true,
      sideBySide: true,
  }

  $('#id_start_time').datetimepicker(dateTimePicker);

  $('#id_start_time_filter').datetimepicker(dateTimePicker);

  $('#id_start_time__lte').datetimepicker(dateTimePicker);

  $('#id_start_time__gte').datetimepicker(dateTimePicker);

  // Every 5 minutes, automatically reload the page.
  // FIXME: Reload only the service data in the table instead of the entire page
  function autoReload() {
    setTimeout(function() {
      $.ajax({
        url: window.location.href,
        success: function() {
          window.location.reload(true);
        }
      });
      autoReload();
   }, 300000);
  }

  autoReload();

});
