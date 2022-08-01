function plot_figure(myChart, details, x_label, samples, tps, avg_rt, min_rt, max_rt, error) {
    let samples_sorted = [...samples];
    let tps_sorted = [...tps];
    let avg_rt_sorted = [...avg_rt];
    let min_rt_sorted = [...min_rt];
    let max_rt_sorted = [...max_rt];
    let error_sorted = [...error];

    samples_sorted.sort(function (a, b) {return a - b});
    tps_sorted.sort(function (a, b) {return a - b});
    avg_rt_sorted.sort(function (a, b) {return a - b});
    min_rt_sorted.sort(function (a, b) {return a - b});
    max_rt_sorted.sort(function (a, b) {return a - b});
    error_sorted.sort(function (a, b) {return a - b});

    option = {
        title: [
            {
                text: 'CPU(%)',
                x: 'center',
                y: 5,
                textStyle: {
                    fontSize: 13
                }
            }
        ],

        grid: [
            {
                left: '5%',
                right: '5%',
                top: 50,
                height: 250
            }
        ],

        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },

        color: ['black', 'blue', 'orange', 'green', 'gray', 'red'],
        legend: [
            {
                data: ['Samples', 'TPS', 'RT(Average)', 'RT(Min)', 'RT(Max)', 'ERROR'],
                x: 'center',
                y: 25,
                icon: 'line'
            }
        ],

        dataZoom: [
            {
                xAxisIndex: [0],
                type: 'inside',
                startValue: 0,
                endValue: samples.length
            },
            {
                xAxisIndex: [0],
                type: 'slider',
                startValue: 0,
                endValue: samples.length
            }
        ],

        xAxis: [
            {
                gridIndex: 0,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {
                    alignWithLabel: true,
                    interval: 'auto'
                },
                axisLabel: {
                    interval: 'auto',
                    showMaxLabel: true
                }
            }
        ],

        yAxis: [
            {
                gridIndex: 0,
                name: 'Speed(MB/s)',
                type: 'value',
                max: Math.max(disk_r_sorted.slice(-1)[0], disk_w_sorted.slice(-1)[0]).toFixed(2)
            },
            {
                gridIndex: 0,
                name: 'IO(%)',
                type: 'value',
                max: IO_sorted.slice(-1)[0].toFixed(2)
            }
        ],
        series: [
            {
                name: 'Samples',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'red'
                },
                data: samples
            },
            {
                name: 'TPS',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'blue'
                },
                data: tps
            },
            {
                name: 'RT(Average)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'orange'
                },
                data: avg_rt
            },
            {
                name: 'RT(Min)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'red'
                },
                data: min_rt
            },
            {
                name: 'RT(Max)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'blue'
                },
                data: max_rt
            },
            {
                name: 'ERROR',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {
                    width: 1,
                    color: 'blue'
                },
                data: error
            }
        ]
    };

    myChart.clear();
    myChart.setOption(option);

    // tables1.rows[1].cells[1].innerHTML = cpu_sorted[parseInt(0.75 * cpu_sorted.length)].toFixed(2);
    // tables1.rows[2].cells[1].innerHTML = cpu_sorted[parseInt(0.9 * cpu_sorted.length)].toFixed(2);
    // tables1.rows[3].cells[1].innerHTML = cpu_sorted[parseInt(0.95 * cpu_sorted.length)].toFixed(2);
    // tables1.rows[4].cells[1].innerHTML = cpu_sorted[parseInt(0.99 * cpu_sorted.length)].toFixed(2);

    myChart.on('dataZoom', function (param) {
        let start_index = myChart.getOption().dataZoom[0].startValue;
        let end_index = myChart.getOption().dataZoom[0].endValue;

        // Bubble Sort
        let samples_sorted = samples.slice(start_index, end_index);
        let tps_sorted = tps.slice(start_index, end_index);
        let avg_rt_sorted = avg_rt.slice(start_index, end_index);
        let min_rt_sorted = min_rt.slice(start_index, end_index);
        let max_rt_sorted = max_rt.slice(start_index, end_index);
        let error_sorted = error.slice(start_index, end_index);
        samples_sorted.sort(function (a, b) {return a - b});
        tps_sorted.sort(function (a, b) {return a - b});
        avg_rt_sorted.sort(function (a, b) {return a - b});
        min_rt_sorted.sort(function (a, b) {return a - b});
        max_rt_sorted.sort(function (a, b) {return a - b});
        error_sorted.sort(function (a, b) {return a - b});

        myChart.setOption({
            yAxis: [
            {
                gridIndex: 0,
                name: 'Speed(MB/s)',
                type: 'value',
                max: Math.max(samples_sorted.slice(-1)[0], tps_sorted.slice(-1)[0], error_sorted.slice(-1)[0]).toFixed(2)
            },
            {
                gridIndex: 0,
                name: 'IO(%)',
                type: 'value',
                max: Math.max(avg_rt_sorted.slice(-1)[0], min_rt_sorted.slice(-1)[0], max_rt_sorted.slice(-1)[0]).toFixed(2)
            }
        ],});

        // tables1.rows[1].cells[1].innerHTML = cpu_sorted[parseInt(0.75 * cpu_sorted.length)].toFixed(2);
        // tables1.rows[2].cells[1].innerHTML = cpu_sorted[parseInt(0.9 * cpu_sorted.length)].toFixed(2);
        // tables1.rows[3].cells[1].innerHTML = cpu_sorted[parseInt(0.95 * cpu_sorted.length)].toFixed(2);
        // tables1.rows[4].cells[1].innerHTML = cpu_sorted[parseInt(0.99 * cpu_sorted.length)].toFixed(2);
    });
}

function findMax(arr) {
    let len = arr.length;
    let max = arr[0];
    while (len--) {
        if (arr[len] > max) {
            max = arr[len];
        }
    }
    return max;
}

function findMin(arr) {
    let len = arr.length;
    let min = arr[0];
    while (len--) {
        if (arr[len] < min) {
            min = arr[len];
        }
    }
    return min;
}

function average(arr) {
    let Sum = 0;
    let total = arr.length;
    for (let i=0; i<total; i++) {
        Sum = Sum + arr[i];
    }
    return Sum / total;
}

function quickSort(arr){
    if(arr.length<=1){
        return arr;
    }
    let temp = arr.pop();
    let left = [];
    let right = [];
    for(let i=0;i<arr.length;i++){
        if(arr[i]<temp){
            left.push(arr[i]);
        }else{
            right.push(arr[i]);
        }
    }
    return quickSort(left).concat(temp,quickSort(right));
}
