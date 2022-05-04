function save_controller(url, location_url, group_id) {
    let groupid = document.getElementById('groupid').value;
    let name = document.getElementById('name').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
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
