function edit_plan(url, location_url) {
    let plan_id = document.getElementById('ID').value;
    let name = document.getElementById('name').value;
    let comment = document.getElementById('comment').value;
    let run_type = document.getElementById('run_type').value;
    let schedule = document.getElementById('schedule').value;
    let server_room = document.getElementById('server_room').value;
    let server_num = document.getElementById('server-num').value;
    let target_number = document.getElementById('target_number').value;
    let duration = document.getElementById('duration').value;
    let isDebug = document.getElementById('isDebug').value;
    let time_setting = document.getElementById('time_setting').value;

    let post_data = {
        plan_id: plan_id,
        name: name,
        run_type: run_type,
        schedule: schedule,
        server_room: server_room,
        server_num: server_num,
        target_number: target_number,
        duration: duration,
        is_debug: isDebug,
        time_setting: time_setting,
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

function upload_file(url) {
    let fileUpload_input = document.getElementById("fileUpload-input");
    fileUpload_input.click();

    fileUpload_input.onchange = function (event) {
        $('.modal_cover').css("display", "block");
        $('.modal_gif').css("display", "block");
        let files = event.target.files;
        let total_files = files.length;
        if (total_files < 1) {
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
            return;
        }

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            if(files[i].name.indexOf('.zip') < 2) {
                $.Toast("Only upload '.zip' files", 'error');
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
                return;
            }
            form_data.append("file", files[i]);
            form_data.append("name", files[i].name);
            form_data.append("type", files[i].type ? files[i].type : "");
            form_data.append("size", files[i].size);
            form_data.append("index", i + 1);
            form_data.append("total", total_files);
            console.log(files[i].name);

            $.ajax({
                url: url,
                type: 'post',
                data: form_data,
                processData: false,
                contentType: false,
                dataType: 'json',
                success: function (data) {
                    if(data['code'] === 0) {
                        $.Toast(data['msg'], 'success');
                        window.location.reload();
                    } else {
                        $.Toast(data['msg'], 'error');
                    }
                    $('.modal_cover').css("display", "none");
                    $('.modal_gif').css("display", "none");
                },
                complete: function () {
                    console.log(i);
                }
            })
        }
    }
}

function add_task(url, start_url, location_url, plan_id) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let post_data = {
        plan_id: plan_id,
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                let post_data = {
                    task_id: data['data']}
                $.ajax({
                    type: 'post',
                    url: start_url,
                    data: post_data,
                    dataType: 'json',
                    success: function (data) {
                        if(data['code'] === 0) {
                            $.Toast(data['msg'], 'success');
                            window.location.href = location_url + '?id=' + data['data'];
                        } else {
                            $.Toast(data['msg'], 'error');
                        }
                    }
                })
            } else {
                $.Toast(data['msg'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}

function stop_task(url) {
    $.ajax({
        type: 'get',
        url: url,
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function start_task(url, task_id, status_url, detail_url) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let post_data = {
        task_id: task_id,
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                $.ajax({
                    type: 'get',
                    url: status_url + '?id=' + task_id,
                    success: function (data) {
                        if(data['code'] === 0) {
                            $.Toast(data['msg'], 'success');
                            window.location.href = detail_url + '?id=' + task_id;
                        } else {
                            $.Toast(data['msg'], 'error');
                        }
                    }
                })
            } else {
                $.Toast(data['msg'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}
