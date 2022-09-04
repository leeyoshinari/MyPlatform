function plot(task_id, url) {
    let figure_title = document.getElementById('figure-title').name;
    let post_data = {
        id: task_id,
        host: figure_title
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                $('#figure').removeAttr("_echarts_instance_").empty();
                let figure = document.getElementById('figure');
                let details = document.getElementsByClassName("plan-detail");

                let myChart = echarts.init(figure);
                plot_figure(myChart, details, data['data']['time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
                data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
            } else {
                $.Toast(data['message'], 'error');
                return;
            }
        }
    });
}

function plot_delta(task_id, url, startTime) {
    let post_data = {
        id: task_id,
        startTime: startTime
    };
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                let figure = document.getElementById('figure');
                let myChart = echarts.init(figure);
                plot_delta_figure(myChart, data['data']['time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
                data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
            } else {
                $.Toast(data['message'], 'error');
                return;
            }
        }
    });
}

function get_running_server(task_id, url, status, url1, url2, url3, url4, url5) {
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
                    s += '<tr class="running"><td>' + all_host[i]['host'] + '</td><td>-</td>';
                    if (all_host[i]['cpu']) {
                        s += '<td>' + all_host[i]['cpu'] + 'core(s)/' + all_host[i]['cpu_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['mem']) {
                        s += '<td>' + all_host[i]['mem'] + 'G/' + all_host[i]['mem_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['disk']) {
                        s += '<td>' + all_host[i]['disk'] + '/' + all_host[i]['disk_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['network_speed']) {
                        s += '<td>' + all_host[i]['network_speed'] + 'Mb/s</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['action'] === 1 && status === 1) {
                        s += '<td><a onclick="stop_test(\'' + url5 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Stop</a>' +
                            '<a onclick="change_tps(\'' + url2 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Change TPS</a>' +
                            '<a onclick="download_log(\'' + url3 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Download logs</a>' +
                            '<a onclick="view_host_figure(\'' + url4 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">View</a></td></tr>';
                        server_num += 1;
                    } else {
                        if (status === 1) {
                            s += '<td><a onclick="start_test(\'' + url1 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Start</a>' +
                                '<a onclick="download_log(\'' + url3 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Download logs</a>' +
                                '<a onclick="view_host_figure(\'' + url4 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">View</a></td></tr>';
                        } else {
                            s += '<td><a onclick="download_log(\'' + url3 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">Download logs</a>' +
                                '<a onclick="view_host_figure(\'' + url4 + '\',' + task_id + ',\'' + all_host[i]['host'] + '\')">View</a></td></tr>';
                        }
                    }
                }
                if (server_num > 0) {
                    document.getElementById("total-server").innerText = "(" + server_num + " Running Servers)";
                }
                document.getElementById('tbody').innerHTML = s + document.getElementById('tbody').innerHTML;
            } else {
                $.Toast(data['message'], 'error');
                return;
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
                    s += '<tr class="idling"><td>' + all_host[i]['host'] + '</td><td>-</td>';
                    if (all_host[i]['cpu']) {
                        s += '<td>' + all_host[i]['cpu'] + 'core(s)/' + all_host[i]['cpu_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['mem']) {
                        s += '<td>' + all_host[i]['mem'] + 'G/' + all_host[i]['mem_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['disk']) {
                        s += '<td>' + all_host[i]['disk'] + '/' + all_host[i]['disk_usage'].toFixed(2) + '%</td>';
                    } else {
                        s += '<td></td>';
                    }
                    if (all_host[i]['network_speed']) {
                        s += '<td>' + all_host[i]['network_speed'] + 'Mb/s</td>';
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

}

function view_host_figure(url, task_id, host) {
    let figure_title = document.getElementById('figure-title');
    figure_title.value = '(' + host + ')';
    figure_title.name = host;
    plot(task_id, url);
}
