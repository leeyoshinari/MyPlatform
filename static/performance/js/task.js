function plot(task_id, url) {
    let post_data = {
        id: task_id,
    };
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

function get_running_server(task_id, url, ) {
    $.ajax({
        type: 'get',
        url: url + '?id=' + task_id,
        success: function (data) {
            if (data['code'] === 0) {
                let s = "";
                let all_host = data['data'];
                if (all_host.length > 0) {
                    document.getElementById("total-server").innerText = "(" + all_host.length + " Running Servers)";
                }
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
                    if (all_host[i]['action'] === 1) {
                        s += '<td><a>Offline</a><a>Change TPS</a><a>Download logs</a><a>View</a></td></tr>';
                    } else {
                        s += '<td><a>Online</a><a>Download logs</a><a>View</a></td></tr>';
                    }
                }
                document.getElementById('tbody').innerHTML = s + document.getElementById('tbody').innerHTML;
            } else {
                $.Toast(data['message'], 'error');
                return;
            }
        }
    })
}

function get_idle_server(room_id, url) {
    $.ajax({
        type: 'get',
        url: url,
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
                    s += '<td><a>Online</a><a>Download logs</a></td></tr>';
                }
                document.getElementById('tbody').innerHTML = document.getElementById('tbody').innerHTML + s;
            } else {
                $.Toast(data['message'], 'error');
            }
        }
    })
}

