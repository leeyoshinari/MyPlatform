function preview_timing() {
    let x = [];
    let y = [];
    let current_time = 0;
    let s_t = Date.now();
    let test_type = document.getElementById('run_type').value;
    let duration = document.getElementById('duration').value;
    let target_number = parseInt(document.getElementById('target_number').value);
    if (!duration) {
        $.Toast('Please set duration ~', 'error');
        return;
    }
    if (!target_number) {
        if (test_type === '1') {$.Toast('Please set target TPS ~', 'error');}
        if (test_type === '0') {$.Toast('Please set Thread Num ~', 'error');}
        return;
    }
    let values_div = document.getElementById('add-timing').getElementsByClassName('value-div');
    for (let i=0; i<values_div.length; i++) {
        let input_tag = values_div[i].getElementsByTagName('input');
        s_t = new Date(input_tag[0].value).getTime();
        if (s_t < current_time) {
            $.Toast('Please pay attention to the order of time.', 'error');
            return;
        }
        if (s_t > new Date(values_div[0].getElementsByTagName('input')[0].value).getTime() + parseInt(duration) * 1000) {
            $.Toast(input_tag[0].value.replace('T', ' ') + ' is beyond duration ' + duration + ' Seconds ~', 'error');
            return;
        }
        current_time = s_t;
        x.push(input_tag[0].value.replace('T', ' '));
        if (test_type === '1') {
            y.push(parseInt(input_tag[1].value) * target_number / 100);
        } else {
            y.push(target_number);
        }
    }

    if (test_type === '1') {
        x.unshift(date_to_date(x[0], -60));
        y.unshift(2);
        x.push(timestamp_to_date(new Date(values_div[0].getElementsByTagName('input')[0].value).getTime() + parseInt(duration) * 1000));
        y.push(0);
    }

    let title = 'Thread Number';
    if (test_type === '1') {
        title = 'TPS';
    }

    let modal = document.getElementsByClassName('myModal')[0];
    let close_a = document.getElementsByClassName("close")[0];
    modal.style.display = "block";

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
        grid: [{left: '10%', right: '10%', top: 30, height: 150}],
        tooltip: {trigger: 'axis', axisPointer: {type: 'cross'}},
        yAxis: [{name: title, type: 'value'}],
        xAxis: {
                gridIndex: 0,
                type: 'category',
                boundaryGap: false,
                data: x,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
        series: [
            {
                name: title,
                type: 'line',
                step: 'end',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: y
            }
        ]
    };

    myChart.clear();
    myChart.setOption(option);
}