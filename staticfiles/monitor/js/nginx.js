document.getElementById('endtime').value = date_to_date();
document.getElementById('starttime').value = date_to_date(null, -600);
detail_timer = null;
let myChart = null;

document.getElementById('group').addEventListener('change', function () {get_summary();})
document.getElementById('source').addEventListener('change', function () {get_summary();})
document.getElementById('sort-type').addEventListener('change', function () {get_summary();})
document.getElementById('total-number').addEventListener('change', function () {get_summary();})
document.getElementById('time-period').addEventListener('change', function () {change_period();})
document.getElementById('SearchList').addEventListener('click', function () {get_summary();})

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
function change_period() {
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
        get_summary();
    }
}

function get_summary() {
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
        url: document.getElementById('path-name').name,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                if (data['data'].length > 0) {
                    refresh_list(data['data']);
                    $.Toast(data['msg'], 'success');
                }
            } else {
                    document.getElementsByClassName('figure-region')[0].innerHTML = '';
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
        url: document.getElementById('endtime').name,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                if (data['data']['c_time'].length > 0) {
                    plot_figure(data['data']);
                    document.getElementById('start-time').value = data['data']['time'];
                    if (timePeriod !== '0') {
                        detail_timer = setInterval(function () {
                            get_detail_delta(path);
                        }, 10000);
                    }
                }
                $.Toast(data['msg'], 'success');
            } else {
                $.Toast(data['msg'], 'error');
            }
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
        }
    })
}

function get_detail_delta(path) {
    let groupKey = document.getElementById('group').value;
    if (!groupKey) {
        $.Toast('Please select group first ~', 'warning');
        return;
    }
    let source = document.getElementById('source').value;
    let timePeriod = document.getElementById('time-period').value;
    let startTime = document.getElementById('start-time').value;
    if (timePeriod === '0') {
        return;
    }
    let post_data = {
        groupKey: groupKey,
        source: source,
        timePeriod: timePeriod,
        startTime: startTime,
        path: path
    }
    $.ajax({
        type: 'post',
        url: document.getElementById('endtime').name,
        data: post_data,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                if (data['data']['c_time'].length > 0) {
                    plot_figure_delta(data['data']);
                    document.getElementById('start-time').value = data['data']['time'];
                }
            }
        }
    })
}

function refresh_list(data) {
    let s = '';
    document.getElementsByClassName('figure-region')[0].innerHTML = s;
    for (let i=0; i<data.length; i++) {
        s += '<div class="api-detail"><div class="url-path">' + (i+1) +'. ' + data[i]['path'] + '</div><div class="path-data">' +
            'Total Samples: ' + data[i]['sample'] + ', QPS: ' + data[i]['qps'].toFixed(4) + '/s, RT: ' + data[i]['rt'].toFixed(2) + 'ms, Response Body: ' +
            data[i]['size'].toFixed(2) + 'Mb, Error:' + data[i]['error'] + '</div></div>';
    }
    document.getElementsByClassName('figure-region')[0].innerHTML = s;
    let api_detail = document.getElementsByClassName('api-detail');
    for (let i=0; i<api_detail.length; i++) {
        api_detail[i].onclick = function () {
            show_figure(api_detail[i].getElementsByTagName('div')[0].innerText.split('. ')[1]);
        }
    }
}

function show_figure(path) {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    let timePeriod = document.getElementById('time-period').value;
    modal.style.display = "block";

    close_a.onclick = function() {
        if (timePeriod !== '0') {clearInterval(detail_timer);}
        modal.style.display = "none";
    }
    document.getElementById('path-title').innerText = path;
    get_detail(path);

    window.onclick = function(event) {
        if (event.target === modal) {
            if (timePeriod !== '0') {clearInterval(detail_timer);}
            modal.style.display = "none";
        }
    }
}

function plot_figure(data) {
    $('#preview').removeAttr("_echarts_instance_").empty();
    myChart = echarts.init(document.getElementById('preview'));
    let sizeValue = '57%';
    option = {
        grid: [
            {right: sizeValue, bottom: sizeValue},
            {left: sizeValue, bottom: sizeValue},
            {right: sizeValue, top: sizeValue},
            {left: sizeValue, top: sizeValue}
        ],
        tooltip: {trigger: 'axis', axisPointer: {type: 'cross'}},
        dataZoom: [
            {xAxisIndex: [0, 1, 2, 3], type: 'inside', startValue: 0, endValue: data['c_time'].length, left: '10%', right: '10%'},
            {xAxisIndex: [0, 1, 2, 3], type: 'slider', startValue: 0, endValue: data['c_time'].length, left: '10%', right: '10%'}
        ],
        yAxis: [
            {name: 'QPS(/s)', gridIndex: 0, type: 'value'},
            {name: 'RT(ms)', gridIndex: 1, type: 'value'},
            {name: 'Size(Mbs)', gridIndex: 2, type: 'value'},
            {name: 'Error(times)', gridIndex: 3, type: 'value'},
        ],
        xAxis: [
            {
                gridIndex: 0,
                type: 'category',
                boundaryGap: false,
                data: data['c_time'],
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 1,
                type: 'category',
                boundaryGap: false,
                data: data['c_time'],
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 2,
                type: 'category',
                boundaryGap: false,
                data: data['c_time'],
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 3,
                type: 'category',
                boundaryGap: false,
                data: data['c_time'],
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            }
        ],
        series: [
            {
                name: 'QPS(/s)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: data['qps']
            },
            {
                name: 'RT(ms)',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 1,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: data['rt']
            },
            {
                name: 'Size(Mbs)',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 2,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: data['size']
            },
            {
                name: 'Error(times)',
                type: 'line',
                xAxisIndex: 3,
                yAxisIndex: 3,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: data['error']
            }
        ]
    };
    myChart.clear();
    myChart.setOption(option);
}

function plot_figure_delta(data) {
    options = myChart.getOption();
    for(let i=0; i<data['c_time'].length; i++) {
        options.xAxis[0].data.push(data['c_time'][i]);
        options.xAxis[0].data.shift();
        options.xAxis[1].data.push(data['c_time'][i]);
        options.xAxis[1].data.shift();
        options.xAxis[2].data.push(data['c_time'][i]);
        options.xAxis[2].data.shift();
        options.xAxis[3].data.push(data['c_time'][i]);
        options.xAxis[3].data.shift();
        options.series[0].data.push(data['qps'][i]);
        options.series[0].data.shift();
        options.series[1].data.push(data['rt'][i]);
        options.series[1].data.shift();
        options.series[2].data.push(data['size'][i]);
        options.series[2].data.shift();
        options.series[3].data.push(data['error'][i]);
        options.series[3].data.shift();
    }
    document.getElementById('starttime').value = options.xAxis[0].data[0];
    document.getElementById('endtime').value = options.xAxis[0].data.slice(-1)[0];
    myChart.setOption(options);
}
