function save_group(url, location_url, plan_id) {
    let planid = document.getElementById('planid').value;
    let name = document.getElementById('name').value;
    let ramp_time = document.getElementById('ramp_time').value;
    let comment = document.getElementById('comment').value;
    let file_path = document.getElementById('file_path').name;
    let variable_names = document.getElementById('variable_names').value;
    let delimiter = document.getElementById('delimiter').value;
    let recycle = document.getElementById('recycle').value;
    let share_mode = document.getElementById('share_mode').value;

    let post_data = {
        plan_id: planid,
        name: name,
        ramp_time: ramp_time,
        file_path: file_path,
        variable_names: variable_names,
        delimiter: delimiter,
        recycle: recycle,
        share_mode: share_mode,
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
    let ramp_time = document.getElementById('ramp_time').value;
    let comment = document.getElementById('comment').value;
    let file_path = document.getElementById('file_path').name;
    let variable_names = document.getElementById('variable_names').value;
    let delimiter = document.getElementById('delimiter').value;
    let recycle = document.getElementById('recycle').value;
    let share_mode = document.getElementById('share_mode').value;

    let post_data = {
        id: group_id,
        plan_id: planid,
        name: name,
        ramp_time: ramp_time,
        file_path: file_path,
        variable_names: variable_names,
        delimiter: delimiter,
        recycle: recycle,
        share_mode: share_mode,
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

function save_cookie(url, location_url, plan_id) {
    let cookies = document.getElementsByClassName('row-cookie');
    let s = [];
    for (let i=0; i<cookies.length; i++) {
        let values = cookies[i].getElementsByTagName('input');
        let cookie_dict = {
            name: values[0].value,
            value: values[1].value,
            domain: values[2].value,
            path: values[3].value,
            secure: cookies[i].getElementsByTagName('select')[0].value
        }
        s.push(cookie_dict)
    }

    let post_data = {
        plan_id: plan_id,
        cookies: s
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
    let plan_id = document.getElementById('planid').value;
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
            form_data.append("plan_id", plan_id);

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
                            document.getElementById('download_file').style.display = '';
                            document.getElementById('delete_file').style.display = '';
                            document.getElementById('upload_file').style.display = 'none';
                            let s = res['data'].split('/');
                            document.getElementById('file_path').value = s[s.length-1];
                            document.getElementById('file_path').name = res['data'];
                            let small_div = document.getElementsByClassName('small-div');
                            for(let i=0; i<small_div.length; i++) {
                                small_div[i].style.display = '';
                            }
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

function download_file() {
    window.open(document.getElementById('file_path').name);
}

function delete_file(url, group_id) {
    let post_data = {
        group_id: group_id,
        plan_id: document.getElementById('planid').value,
        file_path: document.getElementById('file_path').name
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                document.getElementById('download_file').style.display = 'none';
                document.getElementById('delete_file').style.display = 'none';
                document.getElementById('upload_file').style.display = '';
                document.getElementById('file_path').name = '';
                document.getElementById('file_path').value = '';
                let small_div = document.getElementsByClassName('small-div');
                for(let i=0; i<small_div.length; i++) {
                    small_div[i].style.display = 'none';
                }
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
