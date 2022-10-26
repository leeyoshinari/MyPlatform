function delete_package(url, package_id) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    $.ajax({
        type: 'GET',
        url: url + '?id=' + package_id,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}

document.getElementById('upload-package').addEventListener('click', function () {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let fileUpload_input = document.getElementById("uploadpackage");
        fileUpload_input.click();

        fileUpload_input.onchange = function (event) {
            $('.modal_cover').css("display", "block");
            $('.modal_gif').css("display", "block");
            let system = document.getElementById('system-version').value;
            let arch = document.getElementById('cpu-arch').value;
            let agent_type = document.getElementById('agent-type').value;
            let files = event.target.files;
            if (files.length < 1) {
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
                return;
            }

            for (let i=0; i<files.length; i++) {
                let form_data = new FormData();
                form_data.append("file", files[i]);
                form_data.append("name", files[i].name);
                form_data.append("type", files[i].type ? files[i].type : "");
                form_data.append("system", system);
                form_data.append("arch", arch);
                form_data.append("agent_type", agent_type);

                let xhr = new XMLHttpRequest();
                xhr.open("POST", "upload", true);

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
                                modal.style.display = "none";
                            }
                        } else {
                            $.Toast('ERROR, Please try again ~', 'error');
                            modal.style.display = "none";
                        }
                        $('.modal_cover').css("display", "none");
                        $('.modal_gif').css("display", "none");
                    }
                }
                xhr.send(form_data);
            }
        }
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
})

function deploy(url, host, package_id, s, a) {
    let system_version = document.getElementById('filter').getElementsByTagName('span')[0].getElementsByTagName('strong')[1].innerText;
    let cpu_arch = document.getElementById('filter').getElementsByTagName('span')[0].getElementsByTagName('strong')[2].innerText;
    if(system_version.toLowerCase().indexOf(s.toLowerCase()) === -1 || cpu_arch.toLowerCase().indexOf(a.toLowerCase()) === -1) {
        let res = confirm('System Version or CPU Arch do not match, Are you sure to deploy yet?')
        if (!res) {
            return;
        }
    }
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let post_data = {
        'host': host,
        "id": package_id,
        'address': window.location.host
    }
    $.ajax({
        type: 'POST',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                $.ajax({
                    type: 'GET',
                    url: url + '?host=' + host + '&id=' + package_id,
                    success: function (data) {
                        if (data['code'] === 0) {
                            $.Toast(data['msg'], 'success');
                            window.location.reload();
                        } else {
                            $.Toast(data['msg'], 'error');
                        }
                        $('.modal_cover').css("display", "none");
                        $('.modal_gif').css("display", "none");
                    }
                })
            } else {
                $.Toast(data['msg'], 'error');
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
            }
        }
    })
}

function stop_deploy(url, host, package_id) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    $.ajax({
        type: 'GET',
        url: url + '?host=' + host + '&id=' + package_id,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.reload();
            } else {
                $.Toast(data['msg'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}
