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
                $.Toast(data['message'], 'success');
            } else {
                $.Toast(data['message'], 'error');
                return;
            }

            $('#figure').removeAttr("_echarts_instance_").empty();
            let figure = document.getElementById('figure');
            let details = document.getElementsByClassName("plan-detail");

            let myChart = echarts.init(figure);
            plot_figure(myChart, details, data['data']['time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
            data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
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
                $.Toast(data['message'], 'success');
            } else {
                $.Toast(data['message'], 'error');
                return;
            }

            let figure = document.getElementById('figure');
            let myChart = echarts.init(figure);
            plot_delta_figure(myChart, data['data']['time'], data['data']['samples'], data['data']['tps'], data['data']['avg_rt'],
            data['data']['min_rt'], data['data']['max_rt'], data['data']['err']);
        }
    });
}