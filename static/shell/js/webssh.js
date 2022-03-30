
let socketURL = 'ws://' + window.location.host + '/shell/open/' ;
let sock = new WebSocket(socketURL);
console.log("websocket connect success ~");

sock.onerror = function(err) {
    console.log(err);
    $.Toast('Session Connect Error ~ ', 'error');
}

sock.onopen =function (event) {
    let storage = {
        cols: get_term_size().cols,
        rows: get_term_size().rows,
        type: 'web',
        host: document.title,
    };
    sock.send(JSON.stringify(storage));
}
let term = new Terminal(
    {
        cols: get_term_size().cols,
        rows: get_term_size().rows,
        scrollback: 520,
        useStyle: true,
        cursorBlink: true,
        theme: {
            cursor: "help",
            lineHeight: 16
        }
    }
);

// 打开 websocket 连接, 打开 web 终端
sock.addEventListener('open', function () {
    term.open(document.getElementById('terminal'));
});

// 读取服务器端发送的数据并写入 web 终端
sock.addEventListener('message', function (recv) {
    let data = JSON.parse(recv.data);
    if (data.code === 0) {
        term.write(data.msg);
    } else {
        $.Toast(data.msg, 'error');
        sock.close();
    }
});

sock.onclose = function (e) {
    sock.close();
    $.Toast('Session is already in CLOSED state ~', 'error');
}

let data_msg = {'code': 0, 'data': null};
let size_msg = {'code': 1, 'cols': null, 'rows': null};

// 向服务器端发送数据
term.on('data', function (data) {
    if (sock.readyState === 3) {
        $.Toast('Session is already in CLOSED state ~', 'error');
    }
    data_msg['data'] = data;
    sock.send(JSON.stringify(data_msg));
});

function set_screen_size() {
    let termnal_screen = document.getElementsByClassName('xterm-screen')[0];
    termnal_screen.style.width = $(window).width() + 'px';
    termnal_screen.style.height = $(window).height() - 31 + 'px';
}

setTimeout(function(){
    set_screen_size();
},600
);

// 监听浏览器窗口, 根据浏览器窗口大小修改终端大小
$(window).resize(function () {
    let cols = get_term_size().cols;
    let rows = get_term_size().rows;
    size_msg['cols'] = cols;
    size_msg['rows'] = rows;
    set_screen_size();
    term.resize(cols, rows);
    sock.send(JSON.stringify(size_msg));
});

window.onunload = function () {
    data_msg['code'] = 2;
    sock.send(JSON.stringify(data_msg));
};

document.onclick = function () {
    if (window.getSelection) {
        document.execCommand('Copy');
    }
};


function get_term_size() {
    let init_width = 8.8;
    let init_height = 19;

    return {
        cols: Math.floor($(window).width() / init_width),
        rows: Math.floor($(window).height() / init_height),
    }
}

function upload_file(path) {
    let fileUpload_input = document.getElementById("fileUpload-input");
    let host = document.title;
    fileUpload_input.click();

    fileUpload_input.onchange = function (event) {
        let progressBar = document.getElementById("progressBar");
        let percentageDiv = document.getElementById("percentage");
        $('.modal_cover').css("display", "block");
        $('.modal_gif').css("display", "block");
        let files = event.target.files;
        let total_files = files.length;
        if (total_files < 1) {
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
            return;
        }
        let current_time = new Date().getTime();
        let success_num = 0;
        let failure_num = 0;
        let failure_file = [];
        progressBar.max = total_files;
        progressBar.value = success_num;
        percentageDiv.innerHTML = (success_num / total_files * 100).toFixed(2) + "%";

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("name", files[i].name);
            form_data.append("type", files[i].type ? files[i].type : "");
            form_data.append("index", i + 1);
            form_data.append("total", total_files);
            form_data.append("host", host);
            form_data.append('remotePath', path);
            form_data.append("uploadTime", current_time);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", "file/upload", true);

            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    // progressBar.max = event.total;
                    // progressBar.value = event.loaded;
                    // percentageDiv.innerHTML = (event.loaded / event.total * 100).toFixed(2) + "%";
                }
            };
            xhr.onload = function(event) {
            }

            xhr.onreadystatechange = function() {
                progressBar.value = success_num;
                percentageDiv.innerHTML = (success_num / total_files * 100).toFixed(2) + "%";
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            success_num += 1;
                        } else {
                            failure_num += 1;
                            failure_file.push(res['data']);
                        }
                    } else {
                        failure_num += 1;
                        failure_file.push(res['data']);
                    }

                    if ((success_num + failure_num) === total_files) {
                        $('.modal_cover').css("display", "none");
                        $('.modal_gif').css("display", "none");
                        let msg = "";
                        let level = "success";
                        if (success_num > 0) {
                            msg += success_num + '个文件上传成功';
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + '个文件上传失败';
                            level = "error";
                        }
                        $.Toast(msg, level);
                        if (failure_num > 0) {
                            let s = "";
                            for (let i=0; i<failure_file.length; i++) {
                                s += "<p>" + failure_file[i] + "</p>";
                            }
                            show_message(s);
                        }
                    }
                }
            }
            xhr.send(form_data);
        }
    }
}

function show_message(file_list) {
    let modal = document.getElementById('failure_file');
    let close_a = document.getElementsByClassName("modal-header")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];
    let display_text = document.getElementsByClassName('modal-body')[0];
    display_text.style.cssText = "margin-left:5%; margin-top:3%;";
    display_text.innerHTML = file_list;

    modal.style.display = "block";

    close_a.onclick = function() {
        display_text.innerHTML = '';
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        display_text.innerHTML = '';
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        display_text.innerHTML = '';
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            display_text.innerHTML = '';
            modal.style.display = "none";
        }
    }
}


function download_file(filePath) {
    let host = document.title;
    window.open('file/download?host=' + host + '&filePath=' + filePath);
}

function float_path(folder) {
    let modal = document.getElementById('modal_input');
    let close_a = document.getElementsByClassName("modal-header")[1];
    let cancel_a = document.getElementsByClassName("cancel")[1];
    let submit_a = document.getElementsByClassName("submit")[1];
    let display_text = document.getElementsByClassName('input-body')[0];

    if(folder === 0) {
        document.getElementById('title-name').innerText = 'The Folder you want to Upload to ';
        display_text.innerHTML = '<div><label>Folder Path：</label><input id="folder_path" type="text" placeholder="Please input Absolute Path of the Folder ..."></div>';
    } else {
        document.getElementById('title-name').innerText = 'The File you want to Download ';
        display_text.innerHTML = '<div><label>File Path：</label><input id="folder_path" type="text" placeholder="Please input Absolute Path of the File ..."></div>';
    }

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        modal.style.display = "none";
        let folder_path = document.getElementById('folder_path').value;
        if (folder === 0) {
            upload_file(folder_path);
        } else {
            download_file(folder_path);
        }
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
}