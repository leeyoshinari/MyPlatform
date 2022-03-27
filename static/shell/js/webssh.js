
function get_term_size() {
    let init_width = 8.8;
    let init_height = 19;

    return {
        cols: Math.floor($(window).width() / init_width),
        rows: Math.floor($(window).height() / init_height),
    }
}

function websocket() {
    let ws_scheme = "ws";
    let socketURL = ws_scheme + '://' + window.location.host + '/shell/open/' ;

    var sock = new WebSocket(socketURL);
    console.log("websocket connect success ~");

    sock.onerror = function(err) {
        console.log(err);
        $.Toast('WebSocket connect error ~ ', 'error');
    }

    let storage = {
        cols: get_term_size().cols,
        rows: get_term_size().rows,
        type: 'web',
        host: document.title,
    }

    sock.onopen =function (event) {
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
        } else if (data.code === 1) {
            $.Toast(data.msg, 'error');
        } else {
            $.Toast(data.msg, 'error');
            sock.close();
        }
    });

    /*
    * status 为 0 时, 将用户输入的数据通过 websocket 传递给后台, data 为传递的数据, 忽略 cols 和 rows 参数
    * status 为 1 时, resize pty ssh 终端大小, cols 为每行显示的最大字数, rows 为每列显示的最大字数, 忽略 data 参数
    */
    let message = {'code': 0, 'data': null, 'cols': null, 'rows': null};

    // 向服务器端发送数据
    term.on('data', function (data) {
        if (sock.readyState === 3) {
            $.Toast('WebSocket is already in CLOSED state ~', 'error');
        }
        message['code'] = 0;
        message['data'] = data;
        sock.send(JSON.stringify(message));
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
        message['code'] = 1;
        message['cols'] = cols;
        message['rows'] = rows;
        console.log(JSON.stringify(message));
        set_screen_size();
        term.resize(cols, rows);
        sock.send(JSON.stringify(message));
    });

    window.onunload = function () {
        message['code'] = 0;
        message['data'] = '我';
        sock.send(JSON.stringify(message));
    };

    document.onclick = function () {
        if (window.getSelection) {
            document.execCommand('Copy');
        }
    };
}


window.onload = websocket();

