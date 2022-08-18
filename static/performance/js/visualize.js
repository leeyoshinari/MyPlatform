function plot_figure(myChart, details, x_label, samples, tps, avg_rt, min_rt, max_rt, error) {
    let min_rt_sorted = [...min_rt];
    let max_rt_sorted = [...max_rt];

    min_rt_sorted.sort(function (a, b) {return a - b});
    max_rt_sorted.sort(function (a, b) {return a - b});

    let duration = (Date.parse(new Date(x_label.slice(-1)[0])) - Date.parse(new Date(x_label[0]))) / 1000;
    let total_sample = sum(samples);
    details[1].getElementsByTagName("span")[0].innerText = tps.slice(-1)[0] + "/s";
    details[4].getElementsByTagName("span")[0].innerText = total_sample;
    details[5].getElementsByTagName("span")[0].innerText = (total_sample / duration).toFixed(2) + "/s";
    details[6].getElementsByTagName("span")[0].innerText = twoArrSumOfProduct(samples, avg_rt, total_sample) + " ms";
    details[7].getElementsByTagName("span")[0].innerText = min_rt_sorted.slice(0, 1)[0] + " ms";
    details[8].getElementsByTagName("span")[0].innerText = max_rt_sorted.slice(-1)[0] + " ms";
    details[9].getElementsByTagName("span")[0].innerText = (sum(error) / total_sample * 100).toFixed(4) + "%";

    option = {
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
        series: [
            {
                name: 'Samples',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'black'
                },
                data: samples
            },
            {
                name: 'TPS',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
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
                emphasis: {focus: 'series'},
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
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'green'
                },
                data: min_rt
            },
            {
                name: 'RT(Max)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'gray'
                },
                data: max_rt
            },
            {
                name: 'ERROR',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'red'
                },
                data: error
            }
        ]
    };

    myChart.clear();
    myChart.setOption(option);

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

        let duration = (Date.parse(new Date(x_label[end_index])) - Date.parse(new Date(x_label[start_index]))) / 1000;
        let total_sample = sum(samples_sorted);
        details[4].getElementsByTagName("span")[0].innerText = total_sample;
        details[5].getElementsByTagName("span")[0].innerText = (total_sample / duration).toFixed(2) + "/s";
        details[6].getElementsByTagName("span")[0].innerText = twoArrSumOfProduct(samples_sorted, avg_rt_sorted, total_sample) + " ms";
        details[9].getElementsByTagName("span")[0].innerText = (sum(error_sorted) / total_sample * 100).toFixed(4) + "%";

        min_rt_sorted.sort(function (a, b) {return a - b});
        max_rt_sorted.sort(function (a, b) {return a - b});

        details[7].getElementsByTagName("span")[0].innerText = min_rt_sorted.slice(0, 1)[0] + " ms";
        details[8].getElementsByTagName("span")[0].innerText = max_rt_sorted.slice(-1)[0] + " ms";

        myChart.setOption({
        });
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

function sum(arr){
    return arr.reduce(function(prev,cur){
        return prev + cur;
    },0);
}

function average(arr) {
    let Sum = 0;
    let total = arr.length;
    for (let i=0; i<total; i++) {
        Sum = Sum + arr[i];
    }
    return Sum / total;
}

function twoArrSumOfProduct(arr1, arr2, baseValue) {
    let sumOfProduct = 0;
    for(let i=0; i<arr1.length; i++) {
        sumOfProduct += arr1[i] * arr2[i] / baseValue;
    }
    return sumOfProduct.toFixed(2);
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

function plot_delta_figure(myChart, x_label, samples, tps, avg_rt, min_rt, max_rt, error) {
    myChart.setOption({
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
        series: [
            {
                name: 'Samples',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'black'
                },
                data: samples
            },
            {
                name: 'TPS',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
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
                emphasis: {focus: 'series'},
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
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'green'
                },
                data: min_rt
            },
            {
                name: 'RT(Max)',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'gray'
                },
                data: max_rt
            },
            {
                name: 'ERROR',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                emphasis: {focus: 'series'},
                lineStyle: {
                    width: 1,
                    color: 'red'
                },
                data: error
            }
        ]
    });
}
