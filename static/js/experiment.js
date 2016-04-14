$( document ).ready(function () {
    $('#startModal').modal('show');


    $('#startExpButton').click(function() {
      //alert( "Handler for .click() called." );
      $('#startModal').modal('hide');
    });
})