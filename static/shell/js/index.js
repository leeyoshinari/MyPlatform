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
function edit_server(server) {
    $.ajax({
        type: 'GET',
        url: 'get/server?id=' + server,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                server_modal(data['data']);
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

document.getElementById('searchServer').addEventListener('click', function () {
    let groupName = document.getElementById('groupName').value;
    let serverName = document.getElementById('serverName').value;
    let to_url = document.getElementById('location').value;
    if (!serverName && !groupName) {
        window.location.href = to_url;
    } else {
        window.location.href = to_url + 'search/server?group=' + groupName + '&server=' + serverName;
    }
})

document.getElementById('addServer').addEventListener('click', function () {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";
    document.getElementById("title-name").innerText = "Add Server";

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
        let ServerRoom = document.getElementById("ServerRoom").value;
        let ServerName = document.getElementById('ServerName').value;
        let ServerIP = document.getElementById('ServerIP').value;
        let Port = document.getElementById('Port').value;
        let UserName = document.getElementById('UserName').value;
        let p = document.getElementById('Password').value;

        if (!GroupName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }
        if (!ServerRoom) {
            $.Toast('Please select server room ~ ', 'error');
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

        $('.modal_cover').css("display", "block");
        $('.modal_gif').css("display", "block");
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
            ServerRoom: ServerRoom,
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
                } else {
                    location.reload();
                }
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            clear_input();
            modal.style.display = "none";
        }
    }
})

function clear_input() {
    document.getElementById('ServerName').value = '';
    document.getElementById('ServerRoom').value = '';
    document.getElementById('ServerIP').value = '';
    document.getElementById('Port').value = '22';
    document.getElementById('UserName').value = 'root';
    document.getElementById('Password').value = '';
}


function deploy(host) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    $.ajax({
        type: 'GET',
        url: 'monitor/deploy?host='+host,
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

function stop_mon(host) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    $.ajax({
        type: 'GET',
        url: 'monitor/stop?host='+host,
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

document.getElementById('addUser').addEventListener('click', function(){
    let modal = document.getElementsByClassName('myModal')[1];
    let close_a = document.getElementsByClassName("close")[1];
    let cancel_a = document.getElementsByClassName("cancel")[1];
    let submit_a = document.getElementsByClassName("submit")[1];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let GroupName = document.getElementById("group_name_1").value;
        let UserName = document.getElementById('user_name_1').value;
        let Operate = document.getElementById('operator').value;

        if (!GroupName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }
        if (!UserName) {
            $.Toast('Please input user name ~ ', 'error');
            return;
        }

        let post_data = {
            GroupName: GroupName,
            UserName: UserName,
            Operator: Operate,
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: 'add/user',
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                    return;
                } else {
                    $.Toast(data['msg'], 'success');
                    modal.style.display = "none";
                }
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
})

document.getElementById('createGroup').addEventListener('click', function () {
    let modal = document.getElementsByClassName('myModal')[2];
    let close_a = document.getElementsByClassName("close")[2];
    let cancel_a = document.getElementsByClassName("cancel")[2];
    let submit_a = document.getElementsByClassName("submit")[2];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let GroupName = document.getElementById("group_name_2").value;

        if (!GroupName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }

        let post_data = {
            GroupName: GroupName,
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: 'create/group',
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                    return;
                } else {
                    $.Toast(data['msg'], 'success');
                    modal.style.display = "none";
                    location.reload();
                }
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
})

document.getElementById('createRoom').addEventListener('click', function () {
    let modal = document.getElementsByClassName('myModal')[3];
    let close_a = document.getElementsByClassName("close")[3];
    let cancel_a = document.getElementsByClassName("cancel")[3];
    let submit_a = document.getElementsByClassName("submit")[3];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let RoomName = document.getElementById("room_name").value;
        let room_type = document.getElementById("room_type").value;

        if (!RoomName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }

        let post_data = {
            roomName: RoomName,
            roomType: room_type
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: 'create/room',
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                    return;
                } else {
                    $.Toast(data['msg'], 'success');
                    modal.style.display = "none";
                    location.reload();
                }
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
})

function server_modal(data) {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";
    document.getElementById("title-name").innerText = "Edit Server";
    let opts = document.getElementById("GroupName").options;
    for(let opt of opts) {
        if(parseInt(opt.value) === data['group']) {
            opt.selected = true;
        }
    }
    opts = document.getElementById("ServerRoom").options;
    for(let opt of opts) {
        if(opt.value === data['room']) {
            opt.selected = true;
        }
    }
    document.getElementById('ID').value = data['id'];
    document.getElementById('ServerName').value = data['name'];
    document.getElementById('ServerIP').value = data['host'];
    document.getElementById('Port').value = data['port'];
    document.getElementById('UserName').value = data['user'];
    document.getElementById('ServerIP').setAttribute('readonly', true);
    document.getElementById('ServerIP').setAttribute('disabled', true);

    close_a.onclick = function() {
        clear_input();
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        clear_input();
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let ServerId = document.getElementById("ID").value;
        let GroupName = document.getElementById("GroupName").value;
        let ServerRoom = document.getElementById("ServerRoom").value;
        let ServerName = document.getElementById('ServerName').value;
        let ServerIP = document.getElementById('ServerIP').value;
        let Port = document.getElementById('Port').value;
        let UserName = document.getElementById('UserName').value;
        let p = document.getElementById('Password').value;

        if (!GroupName) {
            $.Toast('Please select group name ~ ', 'error');
            return;
        }
        if (!ServerRoom) {
            $.Toast('Please select server room ~ ', 'error');
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

        $('.modal_cover').css("display", "block");
        $('.modal_gif').css("display", "block")
        let total = ServerId.length;
        let password = '';
        if (p) {
            for (let i = 0; i < p.length; i++) {
                if (i >= total) {
                    password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(ServerId[i - total]));
                } else {
                    password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(ServerId[i]));
                }
            }
        }

        let post_data = {
            ServerId: ServerId,
            GroupName: GroupName,
            ServerName: ServerName,
            ServerRoom: ServerRoom,
            ServerIP: ServerIP,
            Port: Port,
            UserName: UserName,
            Password: password,
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: 'edit/server',
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                } else {
                    location.reload();
                }
                $('.modal_cover').css("display", "none");
                $('.modal_gif').css("display", "none");
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

