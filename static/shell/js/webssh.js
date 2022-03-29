
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

function upload(){
    let file_info = {'code': 3, 'data': 'manage.py'};
    sock.send(JSON.stringify(file_info));

}
