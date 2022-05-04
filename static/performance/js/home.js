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
