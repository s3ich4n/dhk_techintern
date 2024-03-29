function requestDeleteEvent(event) {
    $.ajax({
            url: '/schedule/events/' + $("#event_id").val() + '/',
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            },
            dataType: 'json',
            method: 'DELETE',
            success: function (data) {
                $('#modal_detail_show').modal('toggle');
                $('#delete_success_modal').modal('toggle');
            },
            error: function (data) {
                $('#fail_modal').modal('toggle');
            }
        });
}