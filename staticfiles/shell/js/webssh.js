let t = document.getElementById('terminal');
let viewport;
let termnal_screen;

let socketURL = 'ws://' + window.location.host + '/shell/open/' ;
let sock = new WebSocket(socketURL);
console.log("websocket connect success ~");

let term = new Terminal(
    {
        convertEol: true,
        scrollback: 500,
        useStyle: true,
        cursorBlink: true,
        theme: {
            cursor: "help",
            lineHeight: 16
        }
    }
);
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);

sock.onerror = function(err) {
    console.log(err);
    $.Toast('Session Connect Error ~ ', 'error');
}

sock.addEventListener('open', function () {
    term.open(document.getElementById('terminal'));
    fitAddon.fit();
    let storage = {
        cols: term.cols,
        rows: term.rows,
        type: 'web',
        host: document.title,
    };
    sock.send(JSON.stringify(storage));
    viewport = document.getElementsByClassName("xterm-viewport")[0];
    termnal_screen = document.getElementsByClassName('xterm-screen')[0];
});

sock.addEventListener('message', function (recv) {
    term.write(recv.data);
});

sock.onclose = function (e) {
    sock.close();
    $.Toast('Session is already in CLOSED state ~', 'error');
}

let data_msg = {'code': 0, 'data': null};
let size_msg = {'code': 1, 'cols': null, 'rows': null};

term.onData(data => {
    if (sock.readyState === 3) {
        $.Toast('Session is already in CLOSED state ~', 'error');
    }
    data_msg['data'] = data;
    sock.send(JSON.stringify(data_msg));
});

setTimeout(function(){
    viewport = document.getElementsByClassName("xterm-viewport")[0];
    termnal_screen = document.getElementsByClassName('xterm-screen')[0];
    resize_term();
},500
);

function resize_term() {
    let w = $(window).width() + viewport.clientWidth - viewport.offsetWidth + 'px';
    let h = $(window).height() - 30 + 'px';
    termnal_screen.style.width = w;
    termnal_screen.style.height = h;
    fitAddon.fit();
    size_msg['cols'] = term.cols;
    size_msg['rows'] = term.rows;
    termnal_screen.style.width = w;
    termnal_screen.style.height = h;
    sock.send(JSON.stringify(size_msg));
}

// 监听浏览器窗口, 根据浏览器窗口大小修改终端大小
$(window).resize(function () {
    resize_term();
});

window.onbeforeunload = function(event) {
    event.returnValue = "Are you sure leave ?";
};
window.onunload = function (event) {
    data_msg['code'] = 2;
    sock.send(JSON.stringify(data_msg));
};

term.attachCustomKeyEventHandler(e => {
  if (e.key === 'v' && e.ctrlKey) {
    return false;
  }
  if (e.key === 'c' && e.ctrlKey) {
      try {
          let selection = document.getElementsByClassName('xterm-selection')[0].getElementsByTagName('div')[0].style.width;
          if (selection === '0px') {
              return true;
          } else {
              document.execCommand('Copy');
              return false;
          }
      } catch (e) {
          return true;
      }
  }
});

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
                            msg += success_num + ' files upload success';
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + ' files upload failure';
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