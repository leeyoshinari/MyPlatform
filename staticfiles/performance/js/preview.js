function preview_timing() {
    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    modal.style.display = "block";

    let x = [];
    let y = [];
    let test_type = document.getElementById('run_type').value;
    let target_number = parseInt(document.getElementById('target_number').value);
    let values_div = document.getElementById('add-timing').getElementsByClassName('value-div');
    for (let i=0; i<values_div.length; i++) {
        let input_tag = values_div[i].getElementsByTagName('input');
        x.push(input_tag[0].value.replace('T', ' '));
        if (test_type === '1') {
            y.push(parseInt(input_tag[1].value) * target_number / 100);
        } else {
            y.push(target_number);
        }
    }

    if (test_type === '1') {
        x.unshift(get_delta_minute(x[0], -600));
        y.unshift(2);
    }

    if (test_type === '1') {
        x.push(get_delta_minute(x.slice(-1)[0], 600));
        y.push(0);
    }

    let title = 'Thread Number';
    if (test_type === '1') {
        title = 'TPS';
    }

    preview(title, x, y);

    close_a.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
}

function preview(title, x, y) {
    $('#preview').removeAttr("_echarts_instance_").empty();
    let figure = document.getElementById('preview');
    let myChart = echarts.init(figure);

    option = {
        grid: [
            {
                left: '10%',
                right: '10%',
                top: 30,
                height: 150
            }
        ],

        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },

        yAxis: [
            {
                name: title,
                type: 'value'
            }
        ],
        xAxis: {
                gridIndex: 0,
                type: 'category',
                boundaryGap: false,
                data: x,
                axisTick: {
                    alignWithLabel: true,
                    interval: 'auto'
                },
                axisLabel: {
                    interval: 'auto',
                    showMaxLabel: true
                }
            },
        series: [
            {
                name: title,
                type: 'line',
                step: 'end',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'red'
                },
                data: y
            }
        ]
    };

    myChart.clear();
    myChart.setOption(option);
}

function get_delta_minute(current_date, delta_second) {
    let timestamp = new Date(current_date).getTime();
    timestamp = timestamp + delta_second * 1000;
    let D = new Date(timestamp);
    let hours = D.getHours();
    let minutes = D.getMinutes();
    let seconds = D.getSeconds();
    let month = D.getMonth() + 1;
    let strDate = D.getDate();

    if (month >= 1 && month <= 9) {
        month = "0" + month;
    }
    if (strDate >= 0 && strDate <= 9) {
        strDate = "0" + strDate;
    }
    if (hours >= 0 && hours <= 9) {
        hours = "0" + hours;
    }
    if (minutes >= 0 && minutes <= 9) {
        minutes = "0" + minutes;
    }
    if (seconds >= 0 && seconds <= 9) {
        seconds = "0" + seconds;
    }
    return D.getFullYear() + '-' + month + '-' + strDate + ' ' + hours + ':' + minutes + ':' + seconds;
}