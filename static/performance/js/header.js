function save_header(url, location_url) {
    let name = document.getElementById('name').value;
    let method = document.getElementById('method').value;
    let comment = document.getElementById('comment').value;
    let headers = document.getElementById('add_headers').getElementsByClassName('value-div');

    let datas = '{';
    let header = {};
    if (headers.length > 0) {
        for (let i = 0; i < headers.length; i++) {
            let values = headers[i].getElementsByTagName('input');
            datas += '"' + values[0].value + '":"' + values[1].value + '",';
        }
        datas = datas.substr(0, datas.length - 1) + '}';
        header = JSON.parse(datas);
    }

    let post_data = {
        name: name,
        method: method,
        header: header,
        comment: comment
    }

    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(post_data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
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

function edit_controller(url, location_url, group_id) {
    let controller_id = document.getElementById('ID').value;
    let groupid = document.getElementById('groupid').value;
    let name = document.getElementById('name').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        id: controller_id,
        group_id: groupid,
        name: name,
        comment: comment
    }

    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = location_url + '?id=' + groupid;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
