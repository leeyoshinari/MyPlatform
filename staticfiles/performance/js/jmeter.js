function edit_plan(url, location_url) {
    let plan_id = document.getElementById('ID').value;
    let name = document.getElementById('name').value;
    let comment = document.getElementById('comment').value;
    let run_type = document.getElementById('run_type').value;
    let schedule = document.getElementById('schedule').value;
    let server_room = document.getElementById('server_room').value;
    let group_id = document.getElementById('group-name').value;
    let server_num = document.getElementById('server-num').value;
    let target_number = document.getElementById('target_number').value;
    let duration = document.getElementById('duration').value;
    let isDebug = document.getElementById('isDebug').value;

    if (!duration) {
        $.Toast('Please set duration ~', 'error');
        return;
    }
    if (!target_number) {
        if (run_type === '1') {$.Toast('Please set target TPS ~', 'error');}
        if (run_type === '0') {$.Toast('Please set Thread Num ~', 'error');}
        return;
    }

    let time_setting = [];
    let current_time = Date.now() + 300000;
    let s_t = Date.now();
    if (schedule === '1') {
        let time_settings = document.getElementById("add-timing").getElementsByClassName("value-div");
        if (time_settings.length < 1) {
            $.Toast('Please set timing ~', 'warning');
            return;
        }
        for (let i=0; i<time_settings.length; i++) {
            let values = time_settings[i].getElementsByTagName("input");
            let timing = values[0].value.replace('T', ' ');
            if (timing.length === 16) {timing = timing + ':00';}
            s_t = new Date(timing).getTime();
            if (s_t < current_time) {
                if (i === 0) {
                    $.Toast('Please set the time for 5 minutes from now.', 'error');
                    return;
                } else {
                    $.Toast('Please pay attention to the order of time.', 'error');
                    return;
                }
            }
            if (s_t > new Date(time_settings[0].getElementsByTagName('input')[0].value).getTime() + parseInt(duration) * 1000) {
                $.Toast(timing + ' is beyond duration ' + duration + ' Seconds ~', 'error');
                return;
            }
            current_time = s_t;
            if (run_type === '1') {
                time_setting.push({"timing": timing, "value": values[1].value});
            } else {
                time_setting.push({"timing": timing});
            }
        }
    }

    let post_data = {
        plan_id: plan_id,
        name: name,
        run_type: run_type,
        schedule: schedule,
        server_room: server_room,
        server_num: server_num,
        group_id: group_id,
        target_number: target_number,
        duration: duration,
        is_debug: isDebug,
        time_setting: time_setting,
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
                if(data['data']['flag'] === 0) {
                    $.Toast(data['msg'], 'success');
                    $.ajax({
                        type: 'get',
                        url: 'task/autoRun',
                        dataType: 'json',
                        success: function (data) {
                        }
                    })
                    $('.modal_cover').css("display", "none");
                    $('.modal_gif').css("display", "none");
                    return;
                }
                let post_data = {task_id: data['data']['taskId']}
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

function add_timing() {
    let current_date = get_current_date();
    let c = document.getElementById('add-timing');
    if (document.getElementById('run_type').value === '0') {
        if (c.getElementsByTagName('div').length < 1) {
            let s = '<div class="value-div" style="margin-left: 32%; margin-top: 1%; width: 52%;"><label>StartTime: </label>' +
                '<input type="datetime-local" step="1" min="' + current_date + '" style="width: 26%;" value="">';
            c.appendChild(document.createRange().createContextualFragment(s));
        } else {
            $.Toast('Only need to set one start time ~', 'success');
        }
    } else {
        let s = '<div class="value-div" style="margin-left: 32%; margin-top: 1%; width: 52%;"><label>Time: </label>' +
            '<input type="datetime-local" step="1" min="' + current_date + '" style="width: 26%;" value="">' +
            '<label style="margin-left: 3%;">TPS: </label><input type="text" placeholder="Please input TPS ratio (%)" ' +
            'style="width: 26%;" value=""></div>';
        c.appendChild(document.createRange().createContextualFragment(s));
    }
}

function del_timing () {
    let c = document.getElementById('add-timing');
    let div = c.getElementsByTagName('div');
    if(div.length > 0) {
        c.removeChild(div[div.length - 1]);
    }
}
