function add_plan(url, location_url) {
    let name = document.getElementById('name').value;
    let teardown = document.getElementById('tearDown').value;
    let serialize = document.getElementById('serialize').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        name: name,
        teardown: teardown,
        serialize: serialize,
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
                window.location.href = location_url;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function edit_plan(url, location_url) {
    let plan_id = document.getElementById('ID').value;
    let name = document.getElementById('name').value;
    let teardown = document.getElementById('tearDown').value;
    let serialize = document.getElementById('serialize').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        plan_id: plan_id,
        name: name,
        teardown: teardown,
        serialize: serialize,
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
                window.location.href = location_url;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function save_var(url, location_url, plan_id) {
    let name = document.getElementById('name').value;
    let value = document.getElementById('value').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        plan_id: plan_id,
        name: name,
        value: value,
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
                window.location.href = location_url + '?id=' + plan_id;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function edit_var(url, location_url, plan_id) {
    let var_id = document.getElementById('ID').value;
    let name = document.getElementById('name').value;
    let value = document.getElementById('value').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        id: var_id,
        plan_id: plan_id,
        name: name,
        value: value,
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
                window.location.href = location_url + '?id=' + plan_id;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
