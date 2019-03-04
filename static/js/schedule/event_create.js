function initCreateModal(date) {
    let clicked_date = date.format();

    $('#modal-create').modal('show');
    clearCreateModal();
    $("#event-create-input-author").val($("#username-header").text());
    initDefaultDate(clicked_date);
}

function initDefaultDate(date) {
    $('#start-date').val(date);
    $('#start-time').val('17:00');
}

function clearCreateModal() {
    $('#modal-create input.form-control').val('');
    $('#modal-create input.form-control').prop('readonly', false);
    $('#all-day').prop('checked', false);
    $('#modal-create small').text('');

}

function createSchedule() {
    let is_allday = $('#all-day');

    let start_at = $('#start-date').val() + ' ' + $('#start-time').val();
    let end_at = $('#end-date').val() + ' ' + $('#end-time').val();

    let start_at_type = checkDatetimeType('start');
    let end_at_type = checkDatetimeType('end');

    $.post('/schedule/events/', {
        title: $('#modal-create input[name="title"]').val(),
        category: $('#modal-create select[name="category"]').val(),
        author: $('#modal-create input[name="author"]').val(),
        description: $('#modal-create input[name="description"]').val(),
        is_allday: is_allday.prop('checked'),
        start_at: start_at,
        end_at: end_at,
        start_at_type: start_at_type,
        end_at_type: end_at_type,
        csrfmiddlewaretoken: $('#modal-create input[name="csrfmiddlewaretoken"]').val()
    }).done(function (data) {
        $('#modal-create').modal('hide');
        $('#calendar').fullCalendar('renderEvent', {
            id: data['id'],
            title: data['title'],
            start: data['start_at'],
            end: data['end_at'],
            className: data['category'] === '사내' ? 'fc-event-internal' : 'fc-event-external',
            allDay: data['is_allday'],
        })
    }).fail(function (data) {
        $('#modal-create small').text('');
        $.each(data.responseJSON, function (key, value) {
            $('#modal-create small.' + key + '-invalid').text(value);
        });
    });
}

function checkDatetimeType(key) {
    let key_date = $('#' + key + '-date');
    let key_time = $('#' + key + '-time');

    if (key_date.val() === '' && key_time.val() === '') {
        return '';
    } else if (key_date.val() !== '' && key_time.val() === '') {
        return 'date';
    } else if (key_date.val() === '' && key_time.val() !== '') {
        return 'time';
    } else if (key_date.val() !== '' && key_time.val() !== '') {
        return 'datetime';
    }
}

function changeDatetimeReadonly() {
    let checkbox_allday = $('#all-day');
    let allday_checked = checkbox_allday.prop('checked');
    const start_end_time = ['#start-time', '#end-time'];

    if (allday_checked === true) {
        start_end_time.forEach(function (key) {
            $(key).prop('readonly', true);
        });
    } else {
        start_end_time.forEach(function (key) {
            $(key).prop('readonly', false);
        });
    }
}

function appendTimepicker() {
    $('#start-time').timepicker({'timeFormat': 'H:i', 'showOn': null});
    $('#start-time-picker').on('click', function () {
        $('#start-time').timepicker('show');
    });
    $('#end-time').timepicker({'timeFormat': 'H:i', 'showOn': null});
    $('#end-time-picker').on('click', function () {
        $('#end-time').timepicker('show');
    });
}

$(document).ready(function () {
    appendTimepicker();
});

$(document).on('click', '#create_submit_button', function (e) {
    e.preventDefault();
    createSchedule();
});

$(document).on('click', '#all-day', function () {
    changeDatetimeReadonly();
});

$(document).on('click', '#create_cancel_button', function () {
    clearCreateModal();
});
