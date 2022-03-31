function get_connect_info() {
    var name = $.trim($('#name').val());
    var host = $.trim($('#host').val());
    var port = $.trim($('#port').val());
    var user = $.trim($('#user').val());
    var auth = $("input[name='auth']:checked").val();
    var pwd = $.trim($('#password').val());
    var password = window.btoa(pwd); //加密密码传输
    var dockerName = $.trim($('#dockerName').val());
    var ssh_key = null;
    let sshkey_filename = '';
    if (auth === 'key') {
        var pkey = $('#pkey')[0].files[0];
        var csrf = $("[name='csrfmiddlewaretoken']").val();
        var formData = new FormData();

        formData.append('pkey', pkey);
        formData.append('csrfmiddlewaretoken', csrf);

        $.ajax({
            url: '/upload_ssh_key/',
            type: 'post',
            data: formData,
            async: false,
            processData: false,
            contentType: false,
            mimeType: 'multipart/form-data',
            success: function (data) {
                ssh_key = data;
            }
        });
    }

    var connect_info1 = 'host=' + host + '&port=' + port + '&user=' + user + '&auth=' + auth;
    var connect_info2 = '&password=' + password + '&ssh_key=' + ssh_key;
    // var connect_info = connect_info1 + connect_info2;
    //组装为ssh连接参数
    // var ssh_args = `host=${host}`;
    var conn_info={"type":"web","name":name,"host":host,"port":port,"user":user,"pwd":pwd,"docker_name":dockerName}
    return conn_info

}

function delete_server(server) {
    $.ajax({
        type: 'GET',
        url: 'delete/server?id=' + server,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                location.reload();
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function search_server() {
    let groupName = document.getElementById('groupName').value;
    let serverName = document.getElementById('serverName').value;
    if (!serverName && !groupName) {
        window.location.href = '/shell';
    } else {
        window.location.href = '/shell/search/server?group=' + groupName + '&server=' + serverName;
    }
}

function add_server() {
    let modal = document.getElementById('myModal');
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";

    close_a.onclick = function() {
        clear_input();
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        clear_input();
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let GroupName = document.getElementById("GroupName").value;
        let ServerName = document.getElementById('ServerName').value;
        let ServerIP = document.getElementById('ServerIP').value;
        let Port = document.getElementById('Port').value;
        let UserName = document.getElementById('UserName').value;
        let p = document.getElementById('Password').value;

        if (!GroupName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }
        if (!ServerName) {
            $.Toast('Please input server name ~ ', 'error');
            return;
        }
        if (!ServerIP || ServerIP.split('.').length !== 4) {
            $.Toast('Please input server ip ~ ', 'error');
            return;
        }

        let c = new Date().getTime().toString();
        let total = c.length;
        let password = '';
        if (p) {
            for (let i = 0; i < p.length; i++) {
                if (i >= total) {
                    password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(c[i - total]));
                } else {
                    password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(c[i]));
                }
            }
        }

        let post_data = {
            GroupName: GroupName,
            ServerName: ServerName,
            ServerIP: ServerIP,
            Port: Port,
            UserName: UserName,
            Password: password,
            time: parseInt(c)
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: 'add/server',
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                    return;
                } else {
                    location.reload();
                }
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            clear_input();
            modal.style.display = "none";
        }
    }
}

function clear_input() {
    document.getElementById('ServerName').value = '';
    document.getElementById('ServerIP').value = '';
    document.getElementById('Port').value = '22';
    document.getElementById('UserName').value = 'root';
    document.getElementById('Password').value = '';
}

