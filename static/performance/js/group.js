function save_group(url, location_url, plan_id) {
    let planid = document.getElementById('planid').value;
    let name = document.getElementById('name').value;
    let num_threads = document.getElementById('num_threads').value;
    let ramp_time = document.getElementById('ramp_time').value;
    let scheduler = document.getElementById('scheduler').value;
    let duration = document.getElementById('duration').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        plan_id: planid,
        name: name,
        num_threads: num_threads,
        ramp_time: ramp_time,
        scheduler: scheduler,
        duration: duration,
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
                window.location.href = location_url + '?id=' + planid;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function edit_group(url, location_url, plan_id) {
    let group_id = document.getElementById('ID').value;
    let planid = document.getElementById('planid').value;
    let name = document.getElementById('name').value;
    let num_threads = document.getElementById('num_threads').value;
    let ramp_time = document.getElementById('ramp_time').value;
    let scheduler = document.getElementById('scheduler').value;
    let duration = document.getElementById('duration').value;
    let comment = document.getElementById('comment').value;

    let post_data = {
        id: group_id,
        plan_id: planid,
        name: name,
        num_threads: num_threads,
        ramp_time: ramp_time,
        scheduler: scheduler,
        duration: duration,
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
                window.location.href = location_url + '?id=' + planid;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}