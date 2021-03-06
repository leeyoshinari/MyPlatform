function add_plan(url, location_url) {
    let name = document.getElementById('name').value;
    let teardown = document.getElementById('tearDown').value;
    let serialize = document.getElementById('serialize').value;
    let comment = document.getElementById('comment').value;
    let run_type = document.getElementById('run_type').value;
    let schedule = document.getElementById('schedule').value;
    let server_num = document.getElementById('server_num').value;
    // let init_number = document.getElementById('init_number').value;
    let target_number = document.getElementById('target_number').value;
    let duration = document.getElementById('duration').value;
    let time_setting = document.getElementById('time_setting').value;

    let post_data = {
        name: name,
        teardown: teardown,
        serialize: serialize,
        run_type: run_type,
        schedule: schedule,
        server_num: server_num,
        // init_number: init_number,
        target_number: target_number,
        duration: duration,
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

function edit_plan(url, location_url) {
    let plan_id = document.getElementById('ID').value;
    let name = document.getElementById('name').value;
    let teardown = document.getElementById('tearDown').value;
    let serialize = document.getElementById('serialize').value;
    let comment = document.getElementById('comment').value;
    let run_type = document.getElementById('run_type').value;
    let schedule = document.getElementById('schedule').value;
    let server_num = document.getElementById('server_num').value;
    // let init_number = document.getElementById('init_number').value;
    let target_number = document.getElementById('target_number').value;
    let duration = document.getElementById('duration').value;
    let time_setting = document.getElementById('time_setting').value;

    let post_data = {
        plan_id: plan_id,
        name: name,
        teardown: teardown,
        serialize: serialize,
        run_type: run_type,
        schedule: schedule,
        server_num: server_num,
        // init_number: init_number,
        target_number: target_number,
        duration: duration,
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

function save_variable(url, location_url, plan_id) {
    let variables = document.getElementsByClassName('row-var');
    if (variables.length < 1) {
        $.Toast('Please add variable firstly ~', 'warning');
        return;
    }
    let s = [];
    for (let i=0; i<variables.length; i++) {
        let values = variables[i].getElementsByTagName('input');
        let variable_dict = {
            name: values[0].value,
            value: values[1].value,
            comment: values[2].value
        }
        s.push(variable_dict)
    }

    let post_data = {
        plan_id: plan_id,
        variables: s
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
            form_data.append("file", files[i]);
            form_data.append("name", files[i].name);
            form_data.append("type", files[i].type ? files[i].type : "");
            form_data.append("size", files[i].size);
            form_data.append("index", i + 1);
            form_data.append("total", total_files);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", url);
            xhr.setRequestHeader("processData", "false");

            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                }
            };
            xhr.onload = function(event) {
            }

            xhr.onreadystatechange = function() {
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            $.Toast(res['msg'], 'success');
                            window.location.reload();
                        } else {
                            $.Toast(res['msg'], 'error');
                        }
                    } else {
                        $.Toast('File Upload Failure ~', 'error');
                    }
                }
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
            }
            xhr.send(form_data);
        }
    }
}

function add_task(url, location_url, plan_id) {
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
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = location_url + '?id=' + plan_id;
            } else {
                $.Toast(data['msg'], 'error');
            }
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

function start_task(url, task_id, plan_id) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let post_data = {
        task_id: task_id,
        plan_id: plan_id
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
