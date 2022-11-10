let data = [{'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},{'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33},
    {'path': '/tencent/monitor/nginx/home', 'sample': 12323, 'size': 2233, 'time':234, 'tps': 232, 'error': 33}];
refresh_list(data);
document.getElementById('endtime').value = date_to_date();
document.getElementById('starttime').value = date_to_date(null, -600);

function date_to_date(current_date=null, delta=0) {
    if (current_date) {
        return format_date(new Date(new Date(current_date).getTime() + delta * 1000));
    } else {
        return format_date(new Date(new Date().getTime() + delta * 1000));
    }
}

function format_date(D) {
    let hours = D.getHours();
    let minutes = D.getMinutes();
    let seconds = D.getSeconds();
    let month = D.getMonth() + 1;
    let strDate = D.getDate();

    if (month >= 1 && month <= 9) {month = "0" + month;}
    if (strDate >= 0 && strDate <= 9) {strDate = "0" + strDate;}
    if (hours >= 0 && hours <= 9) {hours = "0" + hours;}
    if (minutes >= 0 && minutes <= 9) {minutes = "0" + minutes;}
    if (seconds >= 0 && seconds <= 9) {seconds = "0" + seconds;}
    return D.getFullYear() + '-' + month + '-' + strDate + ' ' + hours + ':' + minutes + ':' + seconds;
}
function change_period(url) {
    let tp = document.getElementById('time-period').value;
    if (tp === '0') {
        document.getElementById('starttime').style.display = 'inline';
        document.getElementById('endtime').style.display = 'inline';
        document.getElementById('h-line').style.display = 'inline';
    } else {
        document.getElementById('starttime').style.display = 'none';
        document.getElementById('endtime').style.display = 'none';
        document.getElementById('h-line').style.display = 'none';
        document.getElementById('endtime').value = date_to_date();
        document.getElementById('starttime').value = date_to_date(null, -1 * parseInt(tp));
        get_summary(url);
    }
}

function get_summary(url) {
    let groupKey = document.getElementById('group').value;
    if (!groupKey) {
        $.Toast('Please select group first ~', 'warning');
        return;
    }
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let source = document.getElementById('source').value;
    let sortKey = document.getElementById('sort-type').value;
    let limitNum = document.getElementById('total-number').value;
    let timePeriod = document.getElementById('time-period').value;
    let startTime = document.getElementById('starttime').value;
    let endTime = document.getElementById('endtime').value;
    let path = document.getElementById('path-name').value;
    let post_data = {
        groupKey: groupKey,
        source: source,
        sortKey: sortKey,
        limitNum: limitNum,
        timePeriod: timePeriod,
        startTime: startTime,
        endTime: endTime,
        path: path
    }
    $.ajax({
        type: 'post',
        url: url,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                if (data['data'].length > 0) {
                    refresh_list(data['data']);
                    $.Toast(data['msg'], 'success');
                }
            } else {
                    $.Toast(data['msg'], 'error');
                }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}


function get_detail(path) {
    let groupKey = document.getElementById('group').value;
    if (!groupKey) {
        $.Toast('Please select group first ~', 'warning');
        return;
    }
    $('.modal_cover').css("display", "block");
    $('.modal_gif').css("display", "block");
    let source = document.getElementById('source').value;
    let timePeriod = document.getElementById('time-period').value;
    let startTime = document.getElementById('starttime').value;
    let endTime = document.getElementById('endtime').value;
    let post_data = {
        groupKey: groupKey,
        source: source,
        timePeriod: timePeriod,
        startTime: startTime,
        endTime: endTime,
        path: path
    }
    $.ajax({
        type: 'post',
        url: document.getElementById('path-name').name,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                plot_figure(data['data']);
                if (timePeriod !== '0') {
                    let detail_timer = setInterval(function () {
                        get_detail_delta(path);
                    }, 10000);
                }
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function get_detail_delta(path) {
}

function refresh_list(data) {
    let s = '';
    for (let i=0; i<data.length; i++) {
        s += '<div class="api-detail"><div class="url-path">' + (i+1) +'、' + data[i]['path'] + '</div><div class="path-data">' +
            'Total Samples: ' + data[i]['sample'] + ', QPS: ' + data[i]['qps'] + '/s, Time: ' + data[i]['rt'] + 'ms, Size: ' +
            data[i]['size'] + 'Mb, Error:' + data[i]['error'] + '</div></div>';
    }
    document.getElementsByClassName('figure-region')[0].innerHTML = s;
    let api_detail = document.getElementsByClassName('api-detail');
    for (let i=0; i<api_detail.length; i++) {
        api_detail[i].onclick = function () {
            show_figure();
        }
    }
}

function show_figure() {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let timePeriod = document.getElementById('time-period').value;
    modal.style.display = "block";

    close_a.onclick = function() {
        if (timePeriod !== '0') {setInterval(detail_timer);}
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            if (timePeriod !== '0') {setInterval(detail_timer);}
            modal.style.display = "none";
        }
    }
}

function plot_figure(data) {
}
