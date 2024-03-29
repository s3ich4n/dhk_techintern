function remindCancel() {
    if (confirm('정말로 취소하시겠습니까?'))
        location.href = '/'
}

function toggleModalFooter(is_submit) {

    if (is_submit) {
        $("#submit_footer").show();
        $("#update_or_delete_footer").hide();
    }
    else {
        $("#submit_footer").hide();
        $("#update_or_delete_footer").show();
    }
}

function changeDetailToUpdateForm(event) {
    /*  상세보기의 각 필드를 input 형식으로 변경 */
    const title = $("#event_title");
    const category = $("#event_category");
    const start_at = $("#event_start_at");
    const end_at = $("#event_end_at");
    const description = $("#event_description");
    const is_allday = $("#event_is_allday");

    const raw_edited_start_at = moment(start_at.text(), TIME_FORMAT_FOR_UI);
    const raw_edited_end_at = moment(end_at.text(), TIME_FORMAT_FOR_UI);
    const formatted_start_at = raw_edited_start_at.format(TIME_FORMAT_FOR_DATETIME_LOCAL);
    const formatted_end_at = raw_edited_end_at.format(TIME_FORMAT_FOR_DATETIME_LOCAL);

    const input_class = 'form-control input-lg';

    const input_title = getElement('input', {
        id: 'input_title',
        klass: input_class,
        value: title.text(),
    });
    title.replaceWith(input_title);

    const input_category = getSelectElement(getEventCategory(), {
        id: 'input_category',
        selected: category.text(),
        klass: input_class,
    });
    category.replaceWith(input_category);

    const input_start_at = getElement('input', {
        id: 'input_start_at',
        klass: input_class,
        value: formatted_start_at,
        type: 'datetime-local',
    });
    start_at.replaceWith(input_start_at);

    const input_end_at = getElement('input', {
        id: 'input_end_at',
        klass: input_class,
        value: formatted_end_at,
        type: 'datetime-local',
    });
    end_at.replaceWith(input_end_at);

    const input_description = getElement('textarea', {
        id: 'input_description',
        klass: input_class,
        value: description.text(),
    });
    description.replaceWith(input_description);

    const input_is_allday = getCheckboxElement(is_allday.prop('checked'), false, {
        id: 'input_is_allday',
        klass: 'form-check-input position-static',
    });
    is_allday.replaceWith(input_is_allday);

    const div_for_common_form_msg = getElement('div', {
        id: 'input_all',
    });
    $("#update_modal_body").append(div_for_common_form_msg);

}

function showFormErrorMessage(xhr) {
    /* 폼 유효성 검사에 통과되지 못할 때 에러메세지를 각 input 아래에 띄움. */
    $(".error_msg").remove();

    const response = JSON.parse(xhr.responseText);
    const form_error = JSON.parse(response['error']);
    const form_error_fields = Object.getOwnPropertyNames(form_error);

    for (let idx in form_error_fields) {
        let field = form_error_fields[idx];
        let field_id = ['#input_', field].join('');
        for (let field_idx in form_error[field]) {
            let err_element = getElement('p', {
                klass: 'error_msg',
            });
            err_element.append(form_error[field][field_idx]["message"]);
            $(field_id).parent().append(err_element);
        }

    }
}

function changeCheckboxStatus(field, updated_data) {
    let updated_element = $('#event_is_allday_cell');
    updated_element.html(getCheckboxElement(updated_data[field], true, {
        id: 'event_is_allday',
        klass: 'form-check-input position-static',
    }));

    let field_dom_id = ['#input_', field].join('');
    $(field_dom_id).replaceWith(updated_element);
}

function requestUpdateEvent(event) {

    const input_title = $("#input_title");
    const input_category = $("#input_category");
    const input_start_at = $("#input_start_at");
    const input_end_at = $("#input_end_at");
    const input_description = $("#input_description");
    const author = $("#event_author");
    const is_allday = $("#input_is_allday");

    const raw_start_at = moment(input_start_at.val(), TIME_FORMAT_FOR_DATETIME_LOCAL);
    const raw_end_at = moment($(input_end_at).val(), TIME_FORMAT_FOR_DATETIME_LOCAL);
    const EVENT_ID = $("#event_id").val();

    $.ajax({
        beforeSend: function (xhr) {
            const csrf_token = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrf_token)
        },
        url: ['/schedule/events/', EVENT_ID, '/edit/'].join(''),
        type: "PUT",
        cache: false,
        contentType: "application/json;charset=UTF-8;",
        data: JSON.stringify({
            "title": input_title.val(),
            "category": input_category.val(),
            "start_at": raw_start_at.format(TIME_FORMAT_FOR_REQUEST),
            "end_at": raw_end_at.format(TIME_FORMAT_FOR_REQUEST),
            "description": input_description.val(),
            "author": author.text(),
            'is_allday': is_allday.prop('checked'),
        }),
        success: function (updated_data) {
            $('.error_msg').remove();

            /* input태그를 td태그로 다시 바꿈. */
            for (let field in updated_data) {
                if (field === 'is_allday') {
                    changeCheckboxStatus(field, updated_data);
                }

                let updated_element = getElement('td', {
                    klass: 'text-center',
                    id: ['event_', field].join(''),
                });
                updated_element.append(updated_data[field] || '');
                let field_dom_id = ['#input_', field].join('');
                $(field_dom_id).replaceWith(updated_element);
            }

            /* datetime을 UI에 맞게 재설정 */
            const updated_start_at = $("#event_start_at");
            const updated_end_at = $("#event_end_at");
            updated_start_at.text(moment(updated_start_at.text()).format(TIME_FORMAT_FOR_UI));
            updated_end_at.text(moment(updated_end_at.text()).format(TIME_FORMAT_FOR_UI));

            toggleModalFooter(false);
        },
        error: function (xhr) {
            if (xhr.status === 403) {
                $('#fail_modal').modal('toggle');
            }
            if (xhr.status === 400) {
                showFormErrorMessage(xhr);
            }
        }
    });
}

