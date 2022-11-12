function plot(myChart, x_label, cpu, iowait, usr_cpu, mem, mem_available, jvm, IO, disk_r, disk_w, disk_d, rec, trans, net, tcp, retrans, port_tcp, close_wait, time_wait, is_jvm) {
    // Quick sort
    /*let cpu_sorted = quickSort(cpu);
    let IO_sorted = quickSort(IO);
    let disk_r_sorted = quickSort(disk_r);
    let disk_w_sorted = quickSort(disk_w);
    let net_sorted = quickSort(net);
    let rec_sorted = quickSort(rec);
    let trans_sorted = quickSort(trans);*/

    // Bubble Sort
    let cpu_sorted = [...cpu];
    let iowait_sorted = [...iowait];
    // let usr_cpu_sorted = [...usr_cpu];
    let IO_sorted = [...IO];
    let disk_r_sorted = [...disk_r];
    let disk_w_sorted = [...disk_w];
    // let disk_d_sorted = [...disk_d];
    let net_sorted = [...net];
    let rec_sorted = [...rec];
    let trans_sorted = [...trans];

    cpu_sorted.sort(function (a, b) {return a - b});
    iowait_sorted.sort(function (a, b) {return a - b});
    // usr_cpu_sorted.sort(function (a, b) {return a - b});
    IO_sorted.sort(function (a, b) {return a - b});
    disk_r_sorted.sort(function (a, b) {return a - b});
    disk_w_sorted.sort(function (a, b) {return a - b});
    // disk_d_sorted.sort(function (a, b) {return a - b});
    net_sorted.sort(function (a, b) {return a - b});
    rec_sorted.sort(function (a, b) {return a - b});
    trans_sorted.sort(function (a, b) {return a - b});

    option = {
        title: [
            {
                text: 'CPU(%), Max: ' + cpu_sorted.slice(-1)[0].toFixed(2) + '%, 90%Line CPU: ' + cpu_sorted[parseInt(0.9 * cpu_sorted.length)].toFixed(2) + '%, 90%Line IOWait: ' + iowait_sorted[parseInt(0.9 * iowait_sorted.length)].toFixed(2) + '%',
                x: 'center',
                y: 5,
                textStyle: {fontSize: 13}
            },
            {
                text: 'Memory(G), Min Available: ' + findMin(mem_available).toFixed(2) + 'G, Min Free: ' + findMin(mem).toFixed(2) + 'G',
                x: 'center',
                y: 305,
                textStyle: {fontSize: 13}
            },
            {
                text: 'IO, Max IO: ' + IO_sorted.slice(-1)[0].toFixed(2) + '%, Avg Read: ' + average(disk_r_sorted).toFixed(2) + 'MB/s, Avg Write: ' + average(disk_w_sorted).toFixed(2) + 'MB/s',
                x: 'center',
                y: 605,
                textStyle: {fontSize: 13}
            },
            {
                text: 'NetWork, Max Net: ' + net_sorted.slice(-1)[0].toFixed(2) + '%, Avg Recv: ' + average(rec_sorted).toFixed(2) + 'MB/s, Avg Trans: ' + average(trans_sorted).toFixed(2) + 'MB/s',
                x: 'center',
                y: 905,
                textStyle: {fontSize: 13}
            },
            {
                text: 'TCP, Max System-TCP: ' + findMax(tcp) + ', Max Port-TCP: '+ findMax(port_tcp),
                x: 'center',
                y: 1205,
                textStyle: {fontSize: 13}
            }
        ],

        grid: [
            {left: '5%', right: '5%', top: 50, height: 200},
            {left: '5%', right: '5%', top: 350, height: 200},
            {left: '5%', right: '5%', top: 650, height: 200},
            {left: '5%', right: '5%', top: 950, height: 200},
            {left: '5%', right: '5%', top: 1250, height: 200}
        ],

        tooltip: {trigger: 'axis', axisPointer: {type: 'cross'}},

        color: ['red', 'blue', 'red', 'orange', 'blue', 'blue', 'orange', 'red', 'orange', 'red', 'red', 'blue', 'orange', 'gray', 'green'],
        legend: [
            {data: ['CPU', 'IOWait'], x: 'center', y: 25, icon: 'line'},
            {data: ['Available', 'Free'], x: 'center', y: 325, icon: 'line'},
            {data: ['rMB/s', 'wMB/s', 'IO'], x: 'center', y: 625, icon: 'line'},
            {data: ['rMB/s', 'tMB/s', 'Net'], x: 'center', y: 925, icon: 'line'},
            {
                data: ['TCP', 'TCP Retrans', 'Port-TCP', 'Time-Wait', 'Close-Wait'],
                x: 'center', y: 1225, icon: 'line'
            }
        ],

        dataZoom: [
            {xAxisIndex: [0, 1, 2, 3, 4], type: 'inside', startValue: 0, endValue: cpu.length},
            {xAxisIndex: [0, 1, 2, 3, 4], type: 'slider', startValue: 0, endValue: cpu.length}
        ],

        xAxis: [
            {
                gridIndex: 0,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 1,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 2,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 3,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            },
            {
                gridIndex: 4,
                type: 'category',
                boundaryGap: false,
                data: x_label,
                axisTick: {alignWithLabel: true, interval: 'auto'},
                axisLabel: {interval: 'auto', showMaxLabel: true}
            }
        ],

        yAxis: [
            {gridIndex: 0, name: 'CPU(%)', type: 'value'},
            {gridIndex: 0},
            {gridIndex: 1, name: 'Memory(G)', type: 'value'},
            {gridIndex: 1},
            {gridIndex: 2, name: 'Speed(MB/s)', type: 'value'},
            {gridIndex: 2, name: 'IO(%)', type: 'value'},
            {gridIndex: 3, name: 'Speed(MB/s)', type: 'value'},
            {gridIndex: 3, name: 'Net(%)', type: 'value'},
            {gridIndex: 4, name: 'TCP', type: 'value',},
            {gridIndex: 4, name: 'TCP Retrans', type: 'value'}
        ],
        series: [
            {
                name: 'CPU',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: cpu
            },
            {
                name: 'IOWait',
                type: 'line',
                xAxisIndex: 0,
                yAxisIndex: 0,
                showSymbol: false,
                lineStyle: {width: 1, color: 'blue'},
                data: iowait
            },
            // {
            //     name: 'Usr',
            //     type: 'line',
            //     xAxisIndex: 0,
            //     yAxisIndex: 0,
            //     showSymbol: false,
            //     lineStyle: {width: 1,color: 'orange'},
            //     data: usr_cpu
            // },
            {
                name: 'Available',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 2,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: mem_available
            },
            {
                name: 'Free',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 2,
                showSymbol: false,
                lineStyle: {width: 1, color: 'orange'},
                data: mem
            },
            {
                name: 'JVM',
                type: 'line',
                xAxisIndex: 1,
                yAxisIndex: 2,
                showSymbol: false,
                lineStyle: {width: 1, color: 'blue'},
                data: []
            },
            {
                name: 'rMB/s',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 4,
                showSymbol: false,
                lineStyle: {width: 1, color: 'blue'},
                data: disk_r
            },
            {
                name: 'wMB/s',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 4,
                showSymbol: false,
                lineStyle: {width: 1, color: 'orange'},
                data: disk_w
            },
            {
                name: 'IO',
                type: 'line',
                xAxisIndex: 2,
                yAxisIndex: 5,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: IO
            },
            {
                name: 'rMB/s',
                type: 'line',
                xAxisIndex: 3,
                yAxisIndex: 6,
                showSymbol: false,
                lineStyle: {width: 1, color: 'blue'},
                data: rec
            },
            {
                name: 'tMB/s',
                type: 'line',
                xAxisIndex: 3,
                yAxisIndex: 6,
                showSymbol: false,
                lineStyle: {width: 1, color: 'orange'},
                data: trans
            },
            {
                name: 'Net',
                type: 'line',
                xAxisIndex: 3,
                yAxisIndex: 7,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: net
            },
            {
                name: 'TCP',
                type: 'line',
                xAxisIndex: 4,
                yAxisIndex: 8,
                showSymbol: false,
                lineStyle: {width: 1, color: 'red'},
                data: tcp
            },
            {
                name: 'TCP Retrans',
                type: 'line',
                xAxisIndex: 4,
                yAxisIndex: 8,
                showSymbol: false,
                lineStyle: {width: 1, color: 'blue'},
                data: retrans
            },
            {
                name: 'Port-TCP',
                type: 'line',
                xAxisIndex: 4,
                yAxisIndex: 9,
                showSymbol: false,
                lineStyle: {width: 1, color: 'orange'},
                data: port_tcp
            },
            {
                name: 'Time-Wait',
                type: 'line',
                xAxisIndex: 4,
                yAxisIndex: 9,
                showSymbol: false,
                lineStyle: {width: 1, color: 'gray'},
                data: time_wait
            },
            {
                name: 'Close-Wait',
                type: 'line',
                xAxisIndex: 4,
                yAxisIndex: 9,
                showSymbol: false,
                lineStyle: {width: 1, color: 'green'},
                data: close_wait
            }
        ]
    };

    if (is_jvm === 1){
        option['title'][1].text = 'Memory(G), Min Available: ' + findMin(mem_available).toFixed(2) + 'G, Min Free: ' + findMin(mem).toFixed(2) + 'G, Max JVM: ' + findMax(jvm).toFixed(2) + 'G';
        option['legend'][1].data = ['Available', 'Free', 'JVM'];
        option['series'][4].data = jvm;
    }

    myChart.clear();
    myChart.setOption(option);

    myChart.on('dataZoom', function (param) {
        let start_index = myChart.getOption().dataZoom[0].startValue;
        let end_index = myChart.getOption().dataZoom[0].endValue;
        // let usr_zoom = usr_cpu.slice(start_index, end_index);
        let mem_zoom = mem.slice(start_index, end_index);
        let mem_a_zoom = mem_available.slice(start_index, end_index);
        let tcp_zoom = tcp.slice(start_index, end_index);
        let port_tcp_zoom = port_tcp.slice(start_index, end_index);
        let mem_title = 'Memory(G), Min Available:: ' + findMin(mem_a_zoom).toFixed(2) + 'G, Min Free:: ' + findMin(mem_zoom).toFixed(2) + 'G';
        if(is_jvm === 1) {
            let jvm_zoom = jvm.slice(start_index, end_index);
            mem_title += ', Max JVM: ' + findMax(jvm_zoom).toFixed(2) + 'G';
        }

        // Bubble Sort
        let cpu_sorted = cpu.slice(start_index, end_index);
        let iowait_sorted = iowait.slice(start_index, end_index);
        let IO_sorted = IO.slice(start_index, end_index);
        let disk_r_sorted = disk_r.slice(start_index, end_index);
        let disk_w_sorted = disk_w.slice(start_index, end_index);
        let rec_sorted = rec.slice(start_index, end_index);
        let trans_sorted = trans.slice(start_index, end_index);
        let net_sorted = net.slice(start_index, end_index);
        cpu_sorted.sort(function (a, b) {return a - b});
        iowait_sorted.sort(function (a, b) {return a - b});
        IO_sorted.sort(function (a, b) {return a - b});
        disk_r_sorted.sort(function (a, b) {return a - b});
        disk_w_sorted.sort(function (a, b) {return a - b});
        net_sorted.sort(function (a, b) {return a - b});
        rec_sorted.sort(function (a, b) {return a - b});
        trans_sorted.sort(function (a, b) {return a - b});

        // Quick Sort
        /*let cpu_sorted = quickSort(cpu.slice(start_index, end_index));
        let IO_sorted = quickSort(IO.slice(start_index, end_index));
        let disk_r_sorted = quickSort(disk_r.slice(start_index, end_index));
        let disk_w_sorted = quickSort(disk_w.slice(start_index, end_index));
        let net_sorted = quickSort(net.slice(start_index, end_index));
        let rec_sorted = quickSort(rec.slice(start_index, end_index));
        let trans_sorted = quickSort(trans.slice(start_index, end_index));*/
        myChart.setOption({
            title: [
                {text: 'CPU(%), Max: ' + cpu_sorted.slice(-1)[0].toFixed(2) + '%, 90%Line CPU: ' + cpu_sorted[parseInt(0.9 * cpu_sorted.length)].toFixed(2) + '%, 90%Line IOWait: ' + iowait_sorted[parseInt(0.9 * iowait_sorted.length)].toFixed(2) + '%', x: 'center', y: 5, textStyle: {fontSize: 13}},
                {text: mem_title, x: 'center', y: 305, textStyle: {fontSize: 13}},
                {text: 'IO, Max IO: ' + IO_sorted.slice(-1)[0].toFixed(2) + '%, Avg Read: ' + average(disk_r_sorted).toFixed(2) + 'MB/s, Avg Write: ' + average(disk_w_sorted).toFixed(2) + 'MB/s', x: 'center', y: 605, textStyle: {fontSize: 13}},
                {text: 'NetWork, Max Net: ' + net_sorted.slice(-1)[0].toFixed(2) + '%, Avg Recv: ' + average(rec_sorted).toFixed(2) + 'MB/s, Avg Trans: ' + average(trans_sorted).toFixed(2) + 'MB/s', x: 'center', y: 905, textStyle: {fontSize: 13}},
                {text: 'TCP, Max System-TCP: ' + findMax(tcp_zoom) + ', Max Port-TCP: '+ findMax(port_tcp_zoom), x: 'center', y: 1205, textStyle: {fontSize: 13}}]});
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

function plot_change(myChart, x_label, cpu, iowait, usr_cpu, mem, mem_available, jvm, IO, disk_r, disk_w, disk_d, rec, trans, net, tcp, retrans, port_tcp, close_wait, time_wait, is_jvm) {
    options = myChart.getOption();
    for(let i=0; i<x_label.length; i++) {
        options.xAxis[0].data.push(x_label[i]);
        options.xAxis[0].data.shift();
        options.xAxis[1].data.push(x_label[i]);
        options.xAxis[1].data.shift();
        options.xAxis[2].data.push(x_label[i]);
        options.xAxis[2].data.shift();
        options.xAxis[3].data.push(x_label[i]);
        options.xAxis[3].data.shift();
        options.xAxis[4].data.push(x_label[i]);
        options.xAxis[4].data.shift();
        options.series[0].data.push(cpu[i]);
        options.series[0].data.shift();
        options.series[1].data.push(iowait[i]);
        options.series[1].data.shift();
        options.series[2].data.push(mem_available[i]);
        options.series[2].data.shift();
        options.series[3].data.push(mem[i]);
        options.series[3].data.shift();
        if (is_jvm === 1) {
            options.series[4].data.push(jvm[i]);
            options.series[4].data.shift();
        }
        options.series[5].data.push(disk_r[i]);
        options.series[5].data.shift();
        options.series[6].data.push(disk_w[i]);
        options.series[6].data.shift();
        options.series[7].data.push(IO[i]);
        options.series[7].data.shift();
        options.series[8].data.push(rec[i]);
        options.series[8].data.shift();
        options.series[9].data.push(trans[i]);
        options.series[9].data.shift();
        options.series[10].data.push(net[i]);
        options.series[10].data.shift();
        options.series[11].data.push(tcp[i]);
        options.series[11].data.shift();
        options.series[12].data.push(retrans[i]);
        options.series[12].data.shift();
        options.series[13].data.push(port_tcp[i]);
        options.series[13].data.shift();
        options.series[14].data.push(time_wait[i]);
        options.series[14].data.shift();
        options.series[15].data.push(close_wait[i]);
        options.series[15].data.shift();
    }
    cpu_sorted = [...options.series[0].data];
    iowait_sorted = [...options.series[1].data];
    cpu_sorted.sort(function (a, b) {return a - b});
    iowait_sorted.sort(function (a, b) {return a - b});
    document.getElementById('starttime').value = options.xAxis[0].data[0];
    document.getElementById('endtime').value = options.xAxis[0].data.slice(-1)[0];
    options.title[0].text = 'CPU(%), Max: ' + cpu_sorted.slice(-1)[0].toFixed(2) + '%, 90%Line CPU: ' + cpu_sorted[parseInt(0.9 * cpu_sorted.length)].toFixed(2) + '%, 90%Line IOWait: ' + iowait_sorted[parseInt(0.9 * iowait_sorted.length)].toFixed(2) + '%';
    myChart.setOption(options);
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
        plot_init('all');
    }
}