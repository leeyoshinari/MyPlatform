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
    let serverRoom = document.getElementById("ServerRoom").value;
    let to_url = document.getElementById('searchServer').name;
    if (!serverName && !groupName && !serverRoom) {
        window.location.href = to_url;
    } else {
        window.location.href = to_url + 'search/server?group=' + groupName + '&server=' + serverName + '&room=' + serverRoom;
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
        let ServerRoom = document.getElementById("Server-room").value;
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
        let GroupKey = document.getElementById("group_identifier_2").value;
        let group_operator = document.getElementById("group_operator").value;
        let group_id = document.getElementById("group_id").value;
        let prefix = document.getElementById("url-prefix").value;

        if (group_operator === 'add' && !GroupName) {
            $.Toast('Please input group name ~ ', 'error');
            return;
        }
        if (group_operator === 'add' && !GroupKey) {
            $.Toast('Please input group unique identifier ~ ', 'error');
            return;
        }

        let post_data = {
            GroupName: GroupName,
            GroupId: group_id,
            GroupType: group_operator,
            GroupKey: GroupKey,
            Prefix: prefix
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: submit_a.name,
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
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
        let room_operator = document.getElementById("room_operator").value;
        let RoomName = document.getElementById("room_name").value;
        let room_type = document.getElementById("room_type").value;
        let room_id = document.getElementById("room_id").value;

        if (room_operator === 'add' && !RoomName) {
            $.Toast('Please input server room name ~ ', 'error');
            return;
        }

        let post_data = {
            roomName: RoomName,
            roomType: room_type,
            operateType: room_operator,
            roomId: room_id
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: submit_a.name,
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
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
    opts = document.getElementById("Server-room").options;
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
        let ServerRoom = document.getElementById("Server-room").value;
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

document.getElementById("group_operator").onchange = function () {
    let operate_type = document.getElementById("group_operator").value;
    if (operate_type === 'add') {
        document.getElementById("group_input").style.display = 'block';
        document.getElementById("group_identifier").style.display = 'block';
        document.getElementById("group_prefix").style.display = 'block';
        document.getElementById("group_select").style.display = 'none';
    } else {
        $.ajax({
            type: 'GET',
            url: document.getElementById("group_id").name,
            success: function (data) {
                if (data['code'] === 0) {
                    let s = '';
                    for (let i=0; i<data['data'].length; i++) {
                        s += '<option value="' + data['data'][i]['pk'] + '">' + data['data'][i]['fields']['name'] + '</option>';
                    }
                    document.getElementById("group_id").innerHTML = s;
                    document.getElementById("group_input").style.display = 'none';
                    document.getElementById("group_identifier").style.display = 'none';
                    document.getElementById("group_prefix").style.display = 'none';
                    document.getElementById("group_select").style.display = 'block';
                } else {
                    $.Toast(data['msg'], 'error');
                }
            }
        })

    }
}

document.getElementById("room_operator").onchange = function () {
    let room_operator = document.getElementById("room_operator").value;
    if (room_operator === 'add') {
        document.getElementById("room_input").style.display = 'block';
        document.getElementById("room_type_select").style.display = 'block';
        document.getElementById("room_id_select").style.display = 'none';
    } else {
        $.ajax({
            type: 'GET',
            url: document.getElementById("room_id").name,
            success: function (data) {
                if (data['code'] === 0) {
                    let s = '';
                    let room_type = ['Used to Applications', 'Used to Middleware', 'Used to Pressure Test'];
                    for (let i=0; i<data['data'].length; i++) {
                        if (data['data'][i]['pk'] === '520') {continue;}
                        s += '<option value="' + data['data'][i]['pk'] + '">' + data['data'][i]['fields']['name'] + ' - ' + room_type[data['data'][i]['fields']['type']] + '</option>';
                    }
                    document.getElementById("room_id").innerHTML = s;
                    document.getElementById("room_input").style.display = 'none';
                    document.getElementById("room_type_select").style.display = 'none';
                    document.getElementById("room_id_select").style.display = 'block';
                }
            }
        })
    }
}
