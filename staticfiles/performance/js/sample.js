function save_sample(url, location_url, group_id) {
    let controllerid = document.getElementById('controllerid').value;
    let name = document.getElementById('name').value;
    let protocol = document.getElementById('protocol').value;
    let domain = document.getElementById('domain').value;
    let port = document.getElementById('port').value;
    let path = document.getElementById('path').value;
    let method = document.getElementById('method').value;
    let http_header = document.getElementById('http_header').value;
    let assertion_type = document.getElementById('assertion_type').value;
    let assertion_string = document.getElementById('assertion_string').value;
    let contentEncoding = document.getElementById('contentEncoding').value;
    let comment = document.getElementById('comment').value;

    let arguments = document.getElementById('add_arguments').getElementsByClassName('value-div');
    let datatype = document.getElementById('data_type').value;
    let datas = '{';
    let argument = {};
    if (arguments.length > 0) {
        for (let i = 0; i < arguments.length; i++) {
            let values = arguments[i].getElementsByTagName('input');
            if (datatype === 'json') {
                datas += '"' + values[0].value + '":"' + values[1].value + '",';
            } else {
                let data_encoding = arguments[i].getElementsByTagName('select')[0].value;
                datas += '"' + values[0].value + '":{"' + values[0].value + '":"' + values[1].value + '","bool_prop_encode":"' + data_encoding + '"},';
            }
        }
        datas = datas.substr(0, datas.length - 1) + '}';
        if (datatype === 'json') {
            argument = JSON.parse('{"request_body_json":' + datas + '}')
        } else {
            argument = JSON.parse(datas);
        }
    }

    let extractors = document.getElementById('add_extractors').getElementsByClassName('value-div');
    let json_extrs = [];
    let regex_extrs = [];
    if (extractors.length > 0) {
        for (let i = 0; i < extractors.length; i++) {
            let values = extractors[i].getElementsByTagName('input');
            if (values[0].value === 'Json') {
                let json_extr = {
                    referenceNames: values[1].value,
                    match_numbers: values[2].value,
                    jsonPathExprs: values[3].value
                }
                json_extrs.push(json_extr);
            } else {
                let regex_extr = {
                    refname: values[1].value,
                    match_number: values[2].value,
                    template: values[3].value,
                    regex: values[4].value
                }
                regex_extrs.push(regex_extr);
            }
        }
    }
    let extractor = {
        json: json_extrs,
        regex: regex_extrs
    }

    let post_data = {
        controller_id: controllerid,
        name: name,
        protocol: protocol,
        domain: domain,
        port: port,
        path: path,
        method: method,
        contentEncoding: contentEncoding,
        http_header: http_header,
        assertion_type: assertion_type,
        assertion_string: assertion_string,
        argument: argument,
        extractor: extractor,
        comment: comment
    }

    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(post_data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = location_url + '?id=' + controllerid;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function edit_sample(url, location_url, group_id) {
    let sample_id = document.getElementById('ID').value;
    let controllerid = document.getElementById('controllerid').value;
    let name = document.getElementById('name').value;
    let protocol = document.getElementById('protocol').value;
    let domain = document.getElementById('domain').value;
    let port = document.getElementById('port').value;
    let path = document.getElementById('path').value;
    let method = document.getElementById('method').value;
    let http_header = document.getElementById('http_header').value;
    let assertion_type = document.getElementById('assertion_type').value;
    let assertion_string = document.getElementById('assertion_string').value;
    let contentEncoding = document.getElementById('contentEncoding').value;
    let comment = document.getElementById('comment').value;

    let arguments = document.getElementById('add_arguments').getElementsByClassName('value-div');
    let datatype = document.getElementById('data_type').value;
    let datas = '{';
    let argument = {};
    if (arguments.length > 0) {
        for (let i = 0; i < arguments.length; i++) {
            let values = arguments[i].getElementsByTagName('input');
            if (datatype === 'json') {
                datas += '"' + values[0].value + '":"' + values[1].value + '",';
            } else {
                let data_encoding = arguments[i].getElementsByTagName('select')[0].value;
                datas += '"' + values[0].value + '":{"' + values[0].value + '":"' + values[1].value + '","bool_prop_encode":"' + data_encoding + '"},';
            }
        }
        datas = datas.substr(0, datas.length - 1) + '}';
        if (datatype === 'json') {
            argument = JSON.parse('{"request_body_json":' + datas + '}')
        } else {
            argument = JSON.parse(datas);
        }
    }

    let extractors = document.getElementById('add_extractors').getElementsByClassName('value-div');
    let json_extrs = [];
    let regex_extrs = [];
    if (extractors.length > 0) {
        for (let i = 0; i < extractors.length; i++) {
            let values = extractors[i].getElementsByTagName('input');
            if (values[0].value === 'Json') {
                let json_extr = {
                    referenceNames: values[1].value,
                    match_numbers: values[2].value,
                    jsonPathExprs: values[3].value
                }
                json_extrs.push(json_extr);
            } else {
                let regex_extr = {
                    refname: values[1].value,
                    match_number: values[2].value,
                    template: values[3].value,
                    regex: values[4].value
                }
                regex_extrs.push(regex_extr);
            }
        }
    }
    let extractor = {
        json: json_extrs,
        regex: regex_extrs
    }

    let post_data = {
        sample_id: sample_id,
        controller_id: controllerid,
        name: name,
        protocol: protocol,
        domain: domain,
        port: port,
        path: path,
        method: method,
        contentEncoding: contentEncoding,
        http_header: http_header,
        assertion_type: assertion_type,
        assertion_string: assertion_string,
        argument: argument,
        extractor: extractor,
        comment: comment
    }

    $.ajax({
        type: 'post',
        url: url,
        data: JSON.stringify(post_data),
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        success: function (data) {
            if(data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = location_url + '?id=' + controllerid;
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function get_header_by_method(url) {
    let method = document.getElementById('method').value;
    $.ajax({
        type: 'get',
        url: url + '?method=' + method,
        dataType: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                let header_obj = document.getElementById('http_header');
                header_obj.options.length = 0;
                for (let i=0; i<data['data'].length; i++) {
                    header_obj.options.add(new Option(data['data'][i]['name'], data['data'][i]['id']));
                }
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
