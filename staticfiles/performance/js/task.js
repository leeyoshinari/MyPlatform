function plot(myChart, task_id, url) {
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let figure_title = document.getElementById('figure-title').name;
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id + '&host=' + figure_title,
        success: function (data) {
            if (data['code'] === 0) {
                let details = document.getElementsByClassName("plan-detail");
                plot_figure(myChart, details, data['data']['c_time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
                data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
                if(data['data']['time'].length > 0) {
                    document.getElementById('start-time').value = data['data']['time'].slice(-1)[0];
                }
            } else {
                $.Toast(data['message'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    });
}

function plot_delta(myChart, task_id, url) {
    let figure_title = document.getElementById('figure-title').name;
    let startTime = document.getElementById('start-time').value;
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id + '&delta=520&host=' + figure_title + '&startTime=' + startTime,
        success: function (data) {
            if (data['code'] === 0) {
                if(data['data']['time'].length > 0) {
                    let details = document.getElementsByClassName("plan-detail");
                    plot_delta_figure(myChart, details, data['data']['c_time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
                    data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
                    document.getElementById('start-time').value = data['data']['time'].slice(-1)[0];
                }
            }
        }
    });
}

function get_running_server(task_id, url, status, url1, url2, url3, url4, url5, plan_type) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id,
        success: function (data) {
            if (data['code'] === 0) {
                let s = "";
                let all_host = data['data'];
                if (all_host.length === 0) {
                    window.location.reload();
                    return;
                }
                let server_num = 0;
                let trs = document.getElementById('tbody').getElementsByClassName('running');
                let trs_length = trs.length;
                for(let i=0; i<trs_length; i++) {
                    trs[0].remove();
                }
                for(let i=0; i<all_host.length; i++) {
                    s += '<tr class="running"><td style="text-align: center;">' + all_host[i]['host'] + '</td><td style="text-align: center;">' + all_host[i]['tps'] + '</td>';
                    if (all_host[i]['cpu']) {
                        s += '<td style="text-align: center;">' + all_host[i]['cpu'] + ' Core(s) / ' + all_host[i]['cpu_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['mem']) {
                        s += '<td style="text-align: center;">' + all_host[i]['mem'] + 'G / ' + all_host[i]['mem_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['disk_size']) {
                        s += '<td style="text-align: center;">' + all_host[i]['disk_size'] + ' / ' + all_host[i]['disk_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['network_speed']) {
                        s += '<td style="text-align: center;">' + all_host[i]['network_speed'] + 'Mb/s</td><td>';
                    } else {
                        s += '<td></td><td>';
                    }
                    if (all_host[i]['action'] === 1 && all_host[i]['status'] === 1 && status === 1) {
                        s += '<a onclick="stop_test(\'' + url5 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Stop</a>';
                        if (plan_type === 1) {
                            s += '<a onclick="change_tps(\'' + url2 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Change TPS</a>';
                        }
                        server_num += 1;
                    }
                    if (status === 1 && all_host[i]['status'] === 0) {
                        s += '<a onclick="start_test(\'' + url1 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Start</a>';
                    }
                    s += '<a target="_blank" href="' + url3 + '?id=' + task_id + '&host=' + all_host[i]['host'] + '">Download logs</a>' +
                         '<a onclick="view_host_figure(\'' + all_host[i]['host'] + '\')">View</a></td></tr>';
                }
                if (server_num > 0) {
                    document.getElementById("total-server").innerText = "(" + server_num + " Running Servers)";
                }
                document.getElementById('tbody').innerHTML = s + document.getElementById('tbody').innerHTML;
            } else {
                $.Toast(data['message'], 'error');
            }
        }
    })
}


function get_used_server(task_id, url, url1) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id,
        success: function (data) {
            if (data['code'] === 0) {
                let s = "";
                let all_host = data['data'];
                let server_num = 0;
                let trs = document.getElementById('tbody').getElementsByClassName('running');
                let trs_length = trs.length;
                for(let i=0; i<trs_length; i++) {
                    trs[0].remove();
                }
                for(let i=0; i<all_host.length; i++) {
                    s += '<tr class="used"><td style="text-align: center;">' + all_host[i]['host'] + '</td><td style="text-align: center;">' + all_host[i]['tps'] + '</td>';
                    if (all_host[i]['cpu']) {
                        s += '<td style="text-align: center;">' + all_host[i]['cpu'] + ' Core(s) / ' + all_host[i]['cpu_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['mem']) {
                        s += '<td style="text-align: center;">' + all_host[i]['mem'] + 'G / ' + all_host[i]['mem_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['disk_size']) {
                        s += '<td style="text-align: center;">' + all_host[i]['disk_size'] + ' / ' + all_host[i]['disk_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['network_speed']) {
                        s += '<td style="text-align: center;">' + all_host[i]['network_speed'] + 'Mb/s</td><td>';
                    } else {
                        s += '<td></td><td>';
                    }
                    s += '<a target="_blank" href="' + url1 + '?id=' + task_id + '&host=' + all_host[i]['host'] + '">Download logs</a>' +
                        '<a onclick="view_host_figure(\'' + all_host[i]['host'] + '\')">View</a></td></tr>';
                    server_num += 1;
                }
                if (server_num > 0) {
                    document.getElementById("total-server").innerText = "(" + server_num + " Servers)";
                }
                document.getElementById('tbody').innerHTML = s + document.getElementById('tbody').innerHTML;
            } else {
                $.Toast(data['message'], 'error');
            }
        }
    })
}

function get_idle_server(room_id, url, task_id, url1) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + room_id,
        success: function (data) {
            if (data['code'] === 0) {
                let s = "";
                let all_host = data['data'];
                for(let i=0; i<all_host.length; i++) {
                    s += '<tr class="idling"><td style="text-align: center;">' + all_host[i]['host'] + '</td><td style="text-align: center;">0</td>';
                    if (all_host[i]['cpu']) {
                        s += '<td style="text-align: center;">' + all_host[i]['cpu'] + ' Core(s) / ' + all_host[i]['cpu_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['mem']) {
                        s += '<td style="text-align: center;">' + all_host[i]['mem'] + 'G / ' + all_host[i]['mem_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['disk_size']) {
                        s += '<td style="text-align: center;">' + all_host[i]['disk_size'] + ' / ' + all_host[i]['disk_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['network_speed']) {
                        s += '<td style="text-align: center;">' + all_host[i]['network_speed'] + 'Mb/s</td>';
                    } else {
                        s += '<td></td>';
                    }
                    s += '<td><a onclick="start_test(\'' + url1 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Start</a></td></tr>';
                }
                document.getElementById('tbody').innerHTML = document.getElementById('tbody').innerHTML + s;
            } else {
                $.Toast(data['message'], 'error');
            }
        }
    })
}

function start_test(url, task_id, host) {
    let post_data = {
        task_id: task_id,
        host: host
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if(data['code'] === 0) {
                let trs = document.getElementById('tbody').getElementsByClassName('idling');
                let trs_length = trs.length;
                for(let i=0; i<trs_length; i++) {
                    trs[0].remove();
                }
                document.getElementById('show-server').innerText = "Show More";
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function stop_test(url, task_id, host) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id + '&host=' + host,
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function download_log(url, task_id, host) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id + '&host=' + host,
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function change_tps(url, task_id, host) {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];
    let total_tps = parseInt(document.getElementById("tps-ratio").name);
    if(host === 'all') {
        document.getElementById('title-name').innerHTML = 'Change Total TPS to';
    } else {
        document.getElementById('title-name').innerHTML = 'Change ' +  host + ' TPS to ';
    }

    modal.style.display = "block";

    document.getElementById("tps-ratio").addEventListener('input', function () {
        let ratio = document.getElementById("tps-ratio").value;
        if (!ratio) {
            ratio = 0;
        }
        let current_tps = parseInt(parseFloat(ratio) / 100 * total_tps);
        if(host === 'all') {
            document.getElementById('title-name').innerHTML = 'Change Total TPS to <span style="color: red;">' + current_tps + '/s</span>';
        } else {
            document.getElementById('title-name').innerHTML = 'Change ' +  host + ' TPS to <span style="color: red;">' + current_tps + '/s</span>';
        }
    })

    close_a.onclick = function() {
        modal.style.display = "none";
        document.getElementById("tps-ratio").value = "";
    }
    cancel_a.onclick = function() {
        modal.style.display = "none";
        document.getElementById("tps-ratio").value = "";
    }

    submit_a.onclick = function() {
        let ratio = document.getElementById("tps-ratio").value;

        if (!ratio) {
            $.Toast('Please input TPS ratio ~ ', 'error');
            return;
        }

        let post_data = {
            taskId: task_id,
            host: host,
            TPS: ratio
        }
        $.ajax({
            type: 'POST',
            async: false,
            url: url,
            data: post_data,
            dataType: 'json',
            success: function (data) {
                if (data['code'] !== 0) {
                    $.Toast(data['msg'], 'error');
                } else {
                    $.Toast(data['msg'], 'success');
                    document.getElementById("tps-ratio").value = "";
                    modal.style.display = "none";
                }
            }
        })
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
            document.getElementById("tps-ratio").value = "";
        }
    }
}
