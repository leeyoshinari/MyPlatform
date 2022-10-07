function search(url) {
    let key_word = document.getElementById('searching').value;
    if(key_word) {
        if (url.indexOf('?') === -1) {
            window.location.href = url + '?keyWord=' + key_word;
        } else {
            window.location.href = url + '&keyWord=' + key_word;
        }
    } else {
        window.location.href = url;
    }
}

function Delete(url, location_url, delete_type, delete_id) {
    if (delete_type === 'header') {
        if (delete_id === 1 || delete_id === 2) {
            $.Toast('Default request header do not be deleted ~', 'warning');
            return;
        }
    }
    let post_data = {
        type: delete_type,
        id: delete_id
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = location_url;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function set_status(set_type, plan_id, is_valid, url) {
    let post_data = {
        id: plan_id,
        set_type: set_type,
        is_valid: is_valid
    }

    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = '';
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function timestamp_to_date(timestamp, delta=0) {
    let D = new Date(timestamp + delta * 1000);
    return format_date(D);
}

function date_to_date(current_date, delta=0) {
    let timestamp = new Date(current_date).getTime();
    let D = new Date(timestamp + delta * 1000);
    return format_date(D);
}

function get_current_date() {
    return format_date(new Date());
}

function format_date(D) {
    let hours = D.getHours();
    let minutes = D.getMinutes();
    let seconds = D.getSeconds();
    let month = D.getMonth() + 1;
    let strDate = D.getDate();

    if (month >= 1 && month <= 9) {month = "0" + month;}
    if (strDate >= 0 && strDate <= 9) {strDate = "0" + strDate;}
    if (hours >= 0 && hours <= 9) {hours = "0" + hours;}
    if (minutes >= 0 && minutes <= 9) {minutes = "0" + minutes;}
    if (seconds >= 0 && seconds <= 9) {seconds = "0" + seconds;}
    return D.getFullYear() + '-' + month + '-' + strDate + ' ' + hours + ':' + minutes + ':' + seconds;
}
