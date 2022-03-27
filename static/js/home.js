// 修改表格行的背景色
let all_icons = {
    "folder": "imageres_3.png",
    "docx": "docx.png",
    "xlsx": "excel.png",
    "pptx": "ppt.png",
    "mp3": "imageres_1004.png",
    "wav": "imageres_1004.png",
    "mp4": "imageres_1005.png",
    "flv": "imageres_1005.png",
    "jpeg": "imageres_1003.png",
    "jpg": "imageres_1003.png",
    "gif": "imageres_1003.png",
    "png": "imageres_1003.png",
    "bmp": "imageres_1003.png",
    "txt": "imageres_1002.png",
    "pdf": "pdf.png"
};
let operate_html = '操作：<button onclick="upload_file()">上传</button><button onclick="op_selected(\'download\')">下载</button><button onclick="create_folder()">新建文件夹</button><button onclick="create_file(\'md\')">新建文件</button><button onclick="op_selected(\'move\')">移动</button><button onclick="op_selected(\'delete\')">删除</button>';
let folder_window = '<div class="modal-content"><div class="modal-header"><span class="close">&times;</span><h2 id="title-name">新建文件夹</h2></div><div class="modal-body"><div><label>名称：</label><input id="folder_name" type="text" placeholder="请输入名称"></div></div><div class="modal-footer"><a class="cancel">取消</a><a class="submit">确定</a></div></div>';
let move_folder = '<div class="move-content"><div class="modal-header"><span class="close">&times;</span><h2 id="title-name">移动文件</h2></div><div class="modal-body"><div><label>移动到目录：</label><input id="folder_name" type="text" placeholder="请选择目标目录" value="/" name="520" readonly></div><div><label>选择目录：</label><div id="folder-tree"><ul class="domtree"><li onclick="get_folders(\'520\')">/</li><ul id="520"></ul></ul></div></div></div><div class="modal-footer"><a class="cancel">取消</a><a class="submit">确定</a></div></div>'
let table_head = '<th width="2%" style="text-align: center;"><input type="checkbox" id="checkout" onclick="checkout_box()"></th><th width="30%">名称</th><th width="10%">大小</th><th width="8%">格式</th><th width="15%">创建时间</th> <th width="15%">修改时间</th><th width="20">操作</th>';
let video_format = 'mp4,avi,flv';
let music_format = 'mp3,wav';
let edit_online = 'txt,md';     // 需要在线编辑的文档
let image_format = 'jpg,jpeg,bmp,png,gif';  // 图标平铺展示，只针对图片
let open_new_tab_format = 'pdf,html';    // 在新标签页打开
let previews = video_format + image_format + music_format + open_new_tab_format;
refresh_folder();
function change_layout(results) {
    let layout = document.getElementById("layout").value;
    if (layout === "0") {
        document.getElementById("layout-table").style.display = "";
        document.getElementById("layout-img").style.display = "none";
        display_files(results);
        // $(".detail").innerHTML
    } else if (layout === "1") {
        document.getElementById("layout-table").style.display = "none";
        document.getElementById("layout-img").style.display = "";
        flat_img(results);
        $(".div-img").css({"width": "350px"});
        $(".checkoutbox input").css({"zoom": "230%"});
    } else if (layout === "2") {
        document.getElementById("layout-table").style.display = "none";
        document.getElementById("layout-img").style.display = "";
        flat_img(results);
        $(".div-img").css({"width": "200px"});
        $(".checkoutbox input").css({"zoom": "150%"});
    } else if (layout === "3") {
        document.getElementById("layout-table").style.display = "none";
        document.getElementById("layout-img").style.display = "";
        flat_img(results);
        $(".div-img").css({"width": "100px"});
        $(".checkoutbox input").css({"zoom": "100%"});
    }
}

function textarea_onfocus(taa) {
    console.log(taa);
}
function textarea_mouseout(file_id, file_type) {
    let file_name = document.getElementById(file_id).value;
    if (file_type === 'folder') {
        rename(file_name, file_id, 'folder/rename');
    } else {
        rename(file_name, file_id, 'file/rename');
    }
}

function create_file(file_format) {
    let folder_id = document.getElementById("current_path").getAttribute("name");
    if (!folder_id) {
        folder_id = 520;
    }
    let post_data = {
        format: file_format,
        folder_id: folder_id
    }

    $.ajax({
        type: "POST",
        url: "file/create",
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                refresh_folder();
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function create_folder() {
    document.getElementById("myModal").innerHTML = folder_window;
    let folder_id = document.getElementById("current_path").getAttribute("name");
    if (!folder_id) {
        folder_id = 520;
    }
    connect_modal(folder_id, '新建文件夹', 'folder/create');
}
function rename_folder(folder_id) {
    document.getElementById("myModal").innerHTML = folder_window;
    connect_modal(folder_id, '重命名文件夹', 'folder/rename');
}
function rename_file(file_id) {
    document.getElementById("myModal").innerHTML = folder_window;
    connect_modal(file_id, '重命名文件', 'file/rename');
}
function connect_modal(folder_id, name, url) {
    document.getElementById('title-name').innerText = name;
    let modal = document.getElementById('myModal');
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let folder_name = document.getElementById("folder_name").value;

        if (!folder_name) {
            $.Toast('请填写文件夹名称哦 ~ ', 'error');
            return;
        }

        rename(folder_name, folder_id, url);
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.innerHTML = '';
            modal.style.display = "none";
        }
    }
}
function op_selected(op) {
    let checkson = document.getElementsByName("selected_file");
    let file_ids = "";
    for (let i=0; i<checkson.length; i++) {
        if (checkson[i].checked) {
            file_ids += checkson[i].value + ',';
        }
    }
    file_ids = file_ids.substr(0, file_ids.length - 1)
    if (!file_ids) {
        $.Toast('请选择文件', 'warning');
        return;
    }
    if (op === 'move') {
        move_to_folder(file_ids, 'file');
    }
    if (op === 'delete') {
        delete_file(file_ids, 0);
    }
    if (op === 'garbage') {
        delete_file(file_ids, 1);
    }
    if (op === 'empty') {
        delete_file(1,9);
    }
    if (op === 'recovery') {
        recovery_file(file_ids)
    }
    if (op === 'download') {
        window.location.href = "file/multiple/download?id=" + file_ids;
    }
}
function move_to_folder(file_id, file_type) {
    let modal = document.getElementById('moving');
    modal.innerHTML = move_folder;
    let close_a = document.getElementsByClassName("close")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    get_folders('520');

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let to_id = document.getElementById("folder_name").name;
        if (file_id.indexOf(to_id) > -1) {
            $.Toast("请不要文件夹移动到自己里面", 'error');
            return;
        }
        let post_data = {
            from_id: file_id,
            to_id: to_id,
            move_type: file_type
        }
        $.ajax({
            type: "POST",
            url: "folder/move",
            data: post_data,
            dataType: "json",
            success: function (data) {
                if (data['code'] === 0) {
                    $.Toast(data['msg'], 'success');
                    refresh_folder();
                } else {
                    $.Toast(data['msg'], 'error');
                    return;
                }
            }
        })

        modal.innerHTML = '';
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.innerHTML = '';
            modal.style.display = "none";
        }
    }
}
function rename(folder_name, folder_id, url) {
    let post_data = {
        name: folder_name,
        id: folder_id
    }

    $.ajax({
        type: "POST",
        url: url,
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                refresh_folder();
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}
function get_root_folder() {
    // 重置文件夹id
    document.getElementById("current_path").setAttribute("name", "520");
    // 重置文件路径
    document.getElementById("current_path").setAttribute("value", "");
    // 重置查询文件格式
    document.getElementById("search").setAttribute("name", "");

    document.getElementById("operation").innerHTML = operate_html;
    let sorted_type = document.getElementById("sort_type").value;
    let sorted = document.getElementById("sorted").value;
    get_files("520", sorted, sorted_type, 1, '', 'file/get');
}
function click_folder(folder_id, name) {
    let current_path = document.getElementById("current_path").getAttribute("value");
    let sorted_type = document.getElementById("sort_type").value;
    let sorted = document.getElementById("sorted").value;
    document.getElementById("current_path").setAttribute("name", folder_id);

    if (!name) {
        document.getElementById("current_path").setAttribute("value", "");
    } else {
        if (current_path) {
            document.getElementById("current_path").setAttribute("value", current_path + ' > ' + name);
        } else {
            document.getElementById("current_path").setAttribute("value", name);
        }
    }
    get_files(folder_id, sorted, sorted_type, 1, '', 'file/get');
}
function refresh_folder(page_num) {
    let folder_id = document.getElementById("current_path").getAttribute("name");
    let file_format = document.getElementById("search").getAttribute("name");
    let sorted_type = document.getElementById("sort_type").value;
    let sorted = document.getElementById("sorted").value;
    if (file_format) {
        get_files(folder_id, sorted, sorted_type, page_num, file_format, 'file/getByFormat');
    }
    else {
        get_files(folder_id, sorted, sorted_type, page_num, file_format, 'file/get');
    }
}
function get_files(folder_id, sorted, sorted_type, page_num, file_format, url) {
    let page_size = 20;
    let layout = document.getElementById("layout").value;
    if (layout === '1') {page_size = 12;}
    if (layout === '2') {page_size = 21;}
    if (layout === '3') {page_size = 50;}
    let post_data = {
        id: folder_id,
        page: page_num,
        format: file_format,
        page_size: page_size,
        sorted: sorted,
        sorted_type: sorted_type
    };

    $.ajax({
        type: "POST",
        url: url,
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                // $.Toast(data['msg'], 'success');
                change_layout(data['data']['data']);
                PagingManage($('#paging'), data['data']['total_page'], data['data']['page'], 'refresh_folder(')
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function recent_file() {
    // 重置文件夹id
    document.getElementById("current_path").setAttribute("name", "520");
    // 重置文件路径
    document.getElementById("current_path").setAttribute("value", "");
    // 重置查询文件格式
    document.getElementById("search").setAttribute("name", "");
    document.getElementById("operation").innerHTML = operate_html;
    let page_size = 20;
    let layout = document.getElementById("layout").value;
    if (layout === '1') {page_size = 12;}
    if (layout === '3') {page_size = 50;}
    $.ajax({
        type: "GET",
        url: "file/get/recent?page=" + page_size,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                change_layout(data['data']);
                $('#paging').html('');
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function display_files(results) {
    document.getElementsByClassName("table_style")[0].innerHTML = table_head;
    document.getElementById("layout-img").innerHTML = "";
    let s = "";
    for (let i=0; i<results.length; i++) {
        if (results[i]['model'] === "myfiles.catalog") {
            s = s + '<tr><td style="text-align: center;"><input type="checkbox" name="selected_folder"></td>';
            s = s + '<td onclick="click_folder(\'' + results[i]['pk'] + '\',\'' + results[i]['fields']['name'] + '\')"><img src="static/img/' + all_icons['folder'] + '">' + results[i]['fields']['name'] + '</td><td></td><td>文件夹</td>';
            s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
            s = s + '<td>' + results[i]['fields']['update_time'].replace('T', ' ') + '</td>';
            s = s + '<td style="white-space: normal;"><button class="actions" onclick="rename_folder(\'' + results[i]['pk'] + '\')">重命名</button><button class="actions" onclick="export_folder(\'' + results[i]['pk'] + '\')">导出</button><button class="actions" onclick="move_to_folder(\'' + results[i]['pk'] + '\', \'folder\')">移动</button><button class="actions" onclick="delete_folder(\'' + results[i]['pk'] + '\')">删除</button></td></tr>';
        }
        if (results[i]['model'] === "myfiles.files") {
            s = s + '<tr><td style="text-align: center;"><input type="checkbox" name="selected_file" value="'+ results[i]['pk'] +'"></td>';
            if (previews.indexOf(results[i]['fields']['format']) > -1) {
                s = s + '<td onclick="show_file(\''+ results[i]['fields']['path'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
            } else if (edit_online.indexOf(results[i]['fields']['format']) > -1) {
                s = s + '<td onclick="show_file(\''+ results[i]['pk'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
            } else {
                s = s + '<td><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
            }
            s = s + '<td>' + beauty_size(results[i]['fields']['size']) + '</td>';
            s = s + '<td>' + results[i]['fields']['format'] + '</td>';
            s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
            s = s + '<td>' + results[i]['fields']['update_time'].replace('T', ' ') + '</td>';
            s = s + '<td style="white-space: normal;"><button class="actions" onclick="rename_file(\'' + results[i]['pk'] + '\')">重命名</button><button class="actions" onclick="download_file(\'' + results[i]['pk'] + '\')">下载</button><button class="actions" onclick="move_to_folder(\'' + results[i]['pk'] + '\', \'file\')">移动</button><button class="actions" onclick="share_file(\'' + results[i]['pk'] + '\')">分享</button><button class="actions" onclick="delete_file(\'' + results[i]['pk'] + '\', 0)">删除</button></td></tr>';
        }
    }
    document.getElementById("tbody").innerHTML = s;
}
function flat_img(results) {
    document.getElementsByClassName("table_style")[0].innerHTML = "";
    document.getElementById("tbody").innerHTML = "";
    let s = "";
    let type_icon = 'folder';
    for (let i=0; i<results.length; i++) {
        if (results[i]['model'] === "myfiles.catalog") {
            s = s + '<div class="div-img"><div onclick="click_folder(\'' + results[i]['pk'] + '\',\'' + results[i]['fields']['name'] + '\')"><img src="static/img/' + all_icons['folder'] + '"></div><div class="checkoutbox"><input type="checkbox"></div>';
            s = s + '<textarea id="' + results[i]['pk'] + '" name="' + type_icon + '" onfocusout="textarea_mouseout(this.id, this.name)" title="' + results[i]['fields']['name'] + '">'+ results[i]['fields']['name'] +'</textarea></div>';
        }
        if (results[i]['model'] === "myfiles.files") {
            let src = 'static/img/' + all_icons[results[i]['fields']['format']];
            if (image_format.indexOf(results[i]['fields']['format']) > -1) {
                src = 'getFile/' + results[i]['fields']['path'];
            }
            s = s + '<div class="div-img"><div><img src="' + src + '"></div><div class="checkoutbox"><input type="checkbox" name="selected_file" value="'+ results[i]['pk'] +'"></div>';
            s = s + '<textarea id="' + results[i]['pk'] + '" name="' + type_icon + '" onfocusout="textarea_mouseout(this.id, this.name)" title="' + results[i]['fields']['name'] + '">' + results[i]['fields']['name'] + '</textarea></div>';
        }
    }
    document.getElementById("layout-img").innerHTML = s;
}

function delete_folder(folder_id) {
    let answer = confirm('确定删除文件夹吗？');
    if (!answer) {
        return;
    }
    $.ajax({
        type: "GET",
        url: "folder/delete?id=" + folder_id,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                refresh_folder();
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}
function delete_file(file_id, is_delete) {
    let answer = "";
    if (is_delete === 0) {
        answer = confirm('确定删除到回收站吗？');
    } else if (is_delete === 6) {
        answer = confirm('确定删除文件分享链接吗？');
    } else {
        answer = confirm('确定删除文件吗？不可恢复哦~');
    }
    if (!answer) {
        return;
    }
    let post_data = {
        type: is_delete,
        file_id: file_id
    }
    $.ajax({
        type: "POST",
        url: "file/delete",
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                if (is_delete === 0) {
                    refresh_folder();
                } else if (is_delete === 6) {
                    get_share_file();
                } else {
                    get_garbage(1);
                }
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}
function search_file(page_num) {
    let word = document.getElementById("search").value.trim();
    if (!word) {
        $.Toast('请输入搜索关键字词', 'warning');
        return;
    }
    // 重置文件夹id
    document.getElementById("current_path").setAttribute("name", "520");
    // 重置文件路径
    document.getElementById("current_path").setAttribute("value", "");
    let page_size = 20;
    let layout = document.getElementById("layout").value;
    if (layout === '1') {page_size = 12;}
    if (layout === '2') {page_size = 21;}
    if (layout === '3') {page_size = 50;}
    let post_data = {
        key_word: word,
        page: page_num,
        page_size: page_size
    }
    $.ajax({
        type: "POST",
        url: "file/search",
        data: post_data,
        dataType: "json",
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                document.getElementsByClassName("table_style")[0].innerHTML = table_head;
                let s = "";
                let results = data['data']['data'];
                for (let i=0; i<results.length; i++) {
                    if (results[i]['model'] === "myfiles.catalog") {
                        s = s + '<tr><td style="text-align: center;"><input type="checkbox" name="selected_folder"></td>';
                        s = s + '<td onclick="click_folder(\'' + results[i]['pk'] + '\',\'' + results[i]['fields']['name'] + '\')"><img src="static/img/' + all_icons['folder'] + '">' + results[i]['fields']['name'] + '</td><td></td><td>文件夹</td>';
                        s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
                        s = s + '<td>' + results[i]['fields']['update_time'].replace('T', ' ') + '</td>';
                        s = s + '<td style="white-space: normal;"><button class="actions" onclick="rename_folder(\'' + results[i]['pk'] + '\')">重命名</button><button class="actions" onclick="move_to_folder(\'' + results[i]['pk'] + '\', \'file\')">移动</button><button class="actions" onclick="delete_folder(\'' + results[i]['pk'] + '\')">删除</button><button class="actions" onclick="find_origin_path(\'' + results[i]['pk'] + '\')">文件位置</button></td></tr>';
                    }
                    if (results[i]['model'] === "myfiles.files") {
                        s = s + '<tr><td style="text-align: center;"><input type="checkbox" name="selected_file" value="'+ results[i]['pk'] +'"></td>';
                        if (previews.indexOf(results[i]['fields']['format']) > -1) {
                            s = s + '<td onclick="show_file(\''+ results[i]['fields']['path'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                        } else if (edit_online.indexOf(results[i]['fields']['format']) > -1) {
                            s = s + '<td onclick="show_file(\''+ results[i]['pk'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                        } else {
                            s = s + '<td><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                        }
                        s = s + '<td>' + beauty_size(results[i]['fields']['size']) + '</td>';
                        s = s + '<td>' + results[i]['fields']['format'] + '</td>';
                        s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
                        s = s + '<td>' + results[i]['fields']['update_time'].replace('T', ' ') + '</td>';
                        s = s + '<td style="white-space: normal;"><button class="actions" onclick="rename_file(\'' + results[i]['pk'] + '\')">重命名</button><button class="actions" onclick="download_file(\'' + results[i]['pk'] + '\')">下载</button><button class="actions" onclick="move_to_folder(\'' + results[i]['pk'] + '\', \'file\')">移动</button><button class="actions" onclick="delete_file(\'' + results[i]['pk'] + '\', 0)">删除</button><button class="actions" onclick="find_origin_path(\'' + results[i]['fields']['parent'] + '\')">文件位置</button></td></tr>';
                    }
                }
                document.getElementById("tbody").innerHTML = s;
                PagingManage($('#paging'), data['data']['total_page'], data['data']['page'], 'search_file(')
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function find_origin_path(folder_id, is_return) {
    $.ajax({
        type: "GET",
        url: "folder/getPath?id=" + folder_id,
        success: function (data) {
            if (data['code'] === 0) {
                if (is_return) {
                    let full_path = data['data'];
                    if (full_path === '当前文件在根目录') {full_path = '/';}
                    document.getElementById("folder_name").setAttribute("value", full_path);
                    document.getElementById("folder_name").setAttribute("name", folder_id);
                } else {
                    $.Toast(data['msg'], 'success');
                    alert('文件路径：' + data['data']);
                }
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function return_folder() {
    let folder_id = document.getElementById("current_path").getAttribute("name");
    let folder_name = document.getElementById("current_path").getAttribute("value");
    if (folder_id === '520') {
        return;
    }
    $.ajax({
        type: "GET",
        url: "folder/return?id=" + folder_id + "&name=" + folder_name,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                document.getElementById("current_path").setAttribute("name", data['data']['id']);
                document.getElementById("current_path").setAttribute("value", data['data']['name']);
                refresh_folder();
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function files_format(file_format) {
    document.getElementById("search").setAttribute("name", file_format);
    // 重置文件夹id
    document.getElementById("current_path").setAttribute("name", "520");
    // 重置文件路径
    document.getElementById("current_path").setAttribute("value", "");

    document.getElementById("operation").innerHTML = operate_html;
    refresh_folder();
}

function get_folders(folder_id) {
    find_origin_path(folder_id, 'folder');
    $.ajax({
        type: "GET",
        url: "folder/get?id=" + folder_id,
        success: function (data) {
            if (data['code'] === 0) {
                let s = '';
                for (let i=0; i<data['data'].length; i++) {
                    s = s + '<li onclick="get_folders(\'' + data['data'][i]['pk'] + '\')">' + data['data'][i]['fields']['name'] + '</li><ul id="' + data['data'][i]['pk'] + '"></ul>'
                }
                document.getElementById(folder_id).innerHTML = s;
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}
function show_message(name, file_list) {
    document.getElementById('title-name').innerText = name;
    let modal = document.getElementById('myModal');
    let close_a = document.getElementsByClassName("modal-header")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];
    let display_text = document.getElementsByClassName('modal-body')[0];
    display_text.style.cssText = "margin-left:5%; margin-top:3%;";
    display_text.innerHTML = file_list;

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.innerHTML = '';
            modal.style.display = "none";
        }
    }
}
function upload_file() {
    let fileUpload_input = document.getElementById("fileUpload-input");
    let folder_id = document.getElementById("current_path").getAttribute("name");
    fileUpload_input.click();

    fileUpload_input.onchange = function (event) {
        let progressBar = document.getElementById("progressBar");
        let percentageDiv = document.getElementById("percentage");
        $('.modal_cover').css("display", "block");
        $('.modal_gif').css("display", "block");
        let files = event.target.files;
        let total_files = files.length;
        if (total_files < 1) {
            $('.modal_cover').css("display", "none");
            $('.modal_gif').css("display", "none");
            return;
        }
        let success_num = 0;
        let fast_upload_num = 0;
        let failure_num = 0;
        let failure_file = [];
        progressBar.max = total_files;
        progressBar.value = success_num;
        percentageDiv.innerHTML = (success_num / total_files * 100).toFixed(2) + "%";

        for (let i=0; i<total_files; i++) {
            let form_data = new FormData();
            form_data.append("file", files[i]);
            form_data.append("name", files[i].name);
            form_data.append("type", files[i].type ? files[i].type : "");
            form_data.append("size", files[i].size);
            form_data.append("index", i + 1);
            form_data.append("total", total_files);
            form_data.append("parent_id", folder_id);

            let xhr = new XMLHttpRequest();
            xhr.open("POST", "file/upload");
            xhr.setRequestHeader("processData", "false");

            xhr.upload.onprogress = function(event) {
                if (event.lengthComputable) {
                    // progressBar.max = event.total;
                    // progressBar.value = event.loaded;
                    // percentageDiv.innerHTML = (event.loaded / event.total * 100).toFixed(2) + "%";
                }
            };
            xhr.onload = function(event) {
            }

            xhr.onreadystatechange = function() {
                progressBar.value = success_num;
                percentageDiv.innerHTML = (success_num / total_files * 100).toFixed(2) + "%";
                if (xhr.readyState === 4) {
                    if(xhr.status === 200) {
                        let res = JSON.parse(xhr.responseText);
                        if (res['code'] === 0) {
                            success_num += 1;
                        } else if (res['code'] === 2) {
                            fast_upload_num += 1;
                        } else {
                            failure_num += 1;
                            failure_file.push(res['data']);
                        }
                    } else {
                        failure_num += 1;
                        failure_file.push(res['data']);
                    }

                    if ((success_num + fast_upload_num + failure_num) === total_files) {
                        $('.modal_cover').css("display", "none");
                        $('.modal_gif').css("display", "none");
                        let msg = "";
                        let level = "success";
                        if (success_num > 0) {
                            msg += success_num + '个文件上传成功';
                        }
                        if (fast_upload_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += fast_upload_num + '个文件已经上传过';
                            level = "warning";
                        }
                        if (failure_num > 0) {
                            if (msg.length > 0) {msg += '，';}
                            msg += failure_num + '个文件上传失败';
                            level = "error";
                        }
                        $.Toast(msg, level);
                        if (failure_num > 0) {
                            let s = "";
                            for (let i=0; i<failure_file.length; i++) {
                                s += "<p>" + failure_file[i] + "</p>";
                            }
                            document.getElementById("myModal").innerHTML = folder_window;
                            show_message("上传失败的文件：", s);
                        }
                        refresh_folder();
                    }
                }
            }
            xhr.send(form_data);
        }
    }
}

function show_file(path, format) {
    if (open_new_tab_format.indexOf(format) > -1) {
        window.open('getFile/' + path);
    } else if (edit_online.indexOf(format) > -1) {
        editor_online(path);
    } else {
        let modal = document.getElementById('myModal');
        modal.innerHTML = folder_window;
        let modal_content = document.getElementsByClassName("modal-content")[0];
        modal_content.style.cssText = "background-color: transparent;";
        modal.style.display = "block";
        if (image_format.indexOf(format) > -1) {
            modal_content.innerHTML = '<img src="getFile/' + path + '">';
        } else if (video_format.indexOf(format) > -1) {
            modal_content.innerHTML = '<link href="static/css/video-js.min.css" rel="stylesheet"><script src="static/js/video.min.js"></script><video id="my_video" class="video-js" controls autoplay preload="none" data-setup="{}"><source src="getFile/' + path + '" type="video/mp4"><track src="getFile/3030/951647768425.ass" srclang="zh" kind="subtitles" label="zh"></video>';
        } else if (music_format.indexOf(format) > -1) {
            modal_content.innerHTML = '<audio id="my_music" controls autoplay preload="none"><source src="getFile/' + path + '" type="audio/mpeg"></audio>';
        }

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.innerHTML = '';
                modal.style.display = "none";
            }
        }
    }
}

function checkout_box() {
    let checked = document.getElementById("checkout").checked;
    let checkson = document.getElementsByName("selected_file");
    if (checked) {
        for (let i = 0; i < checkson.length; i++) {
            checkson[i].checked = true;
        }
    } else {
        for (let i = 0; i < checkson.length; i++) {
            checkson[i].checked = false;
        }
    }
}

function get_garbage(page) {
    document.getElementById("operation").innerHTML = '操作：<button onclick="op_selected(\'garbage\')">删除选中文件</button><button onclick="op_selected(\'recovery\')">还原选中文件</button><button onclick="delete_file(1,9)">清空回收站</button>';
    document.getElementById("layout-img").innerHTML = "";
    $.ajax({
        type: "GET",
        url: "file/garbage?page=" + page,
        success: function (data) {
            if (data['code'] === 0) {
                document.getElementsByClassName("table_style")[0].innerHTML = table_head.substr(0, table_head.length - 22) + '<th width="13%">删除时间</th><th width="7">操作</th>';
                let s = "";
                let results = data['data']['data'];
                for (let i=0; i<results.length; i++) {
                    s = s + '<tr><td style="text-align: center;"><input type="checkbox" name="selected_file" value="'+ results[i]['pk'] +'"></td>';
                    if (previews.indexOf(results[i]['fields']['format']) > -1) {
                        s = s + '<td onclick="show_file(\''+ results[i]['fields']['path'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    } else if (edit_online.indexOf(results[i]['fields']['format']) > -1) {
                        s = s + '<td onclick="show_file(\''+ results[i]['pk'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    } else {
                        s = s + '<td><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    }
                    s = s + '<td>' + beauty_size(results[i]['fields']['size']) + '</td>';
                    s = s + '<td>' + results[i]['fields']['format'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
                    s = s + '<td>' + results[i]['fields']['update_time'].replace('T', ' ') + '</td>';
                    s = s + '<td>' + results[i]['fields']['delete_time'].replace('T', ' ') + '</td>';
                    s = s + '<td><button class="actions" onclick="delete_file(\'' + results[i]['pk'] + '\', 1)">删除</button></td></tr>';
                }
                document.getElementById("tbody").innerHTML = s;
                PagingManage($('#paging'), data['data']['total_page'], data['data']['page'], 'get_garbage(')
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function recovery_file(file_id) {
    $.ajax({
        type: "GET",
        url: "file/recovery?id=" + file_id,
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                get_garbage(1);
            } else {
                $.Toast(data['msg'], 'error');
                return;
            }
        }
    })
}

function download_file(file_id) {
    window.open("file/download?id=" + file_id);
    // $.ajax({
    //     type: "GET",
    //     url: "file/download?id=" + file_id,
    //     success: function (data) {
    //         if (data['code'] === 0) {
    //             $.Toast(data['msg'], 'success');
    //             window.open("getFile/" + data['data']);
    //         } else {
    //             $.Toast(data['msg'], 'error');
    //             return;
    //         }
    //     }
    // })
}
function export_folder(folder_id) {
    window.open("folder/export?id=" + folder_id);
}

function share_file(file_id) {
    let modal = document.getElementById('myModal');
    modal.innerHTML = folder_window;
    document.getElementsByClassName("modal-body")[0].getElementsByTagName("label")[0].innerHTML = '链接打开次数：';
    document.getElementById("folder_name").setAttribute("placeholder", '分享链接打开的最大次数');
    document.getElementById('title-name').innerText = '分享文件 ' + file_id;
    let close_a = document.getElementsByClassName("modal-header")[0];
    let cancel_a = document.getElementsByClassName("cancel")[0];
    let submit_a = document.getElementsByClassName("submit")[0];

    modal.style.display = "block";

    close_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }
    cancel_a.onclick = function() {
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    submit_a.onclick = function() {
        let times = document.getElementById("folder_name").value;

        if (!times) {
            $.Toast('请输入文件分享链接访问次数哦 ~ ', 'error');
            return;
        }

        $.ajax({
            type: "POST",
            url: "file/share",
            data: {file_id: file_id, times: times},
            dataType: "json",
            success: function (data) {
                if (data['code'] === 0) {
                    $.Toast(data['msg'], 'success');
                } else {
                    $.Toast(data['msg'], 'error');
                }
            }
        })
        modal.innerHTML = '';
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.innerHTML = '';
            modal.style.display = "none";
        }
    }
}

function get_share_file() {
    document.getElementById("operation").innerHTML = operate_html;
    $.ajax({
        type: "GET",
        url: "file/getShare",
        success: function (data) {
            if (data['code'] === 0) {
                document.getElementsByClassName("table_style")[0].innerHTML = '<th width="30%">名称</th><th width="10%">已打开次数</th><th width="8%">总次数</th><th width="15%">创建时间</th><th width="20">操作</th>';
                let s = "";
                let results = data['data'];
                for (let i=0; i<results.length; i++) {
                    if (previews.indexOf(results[i]['fields']['format']) > -1) {
                        s = s + '<tr><td onclick="show_file(\''+ results[i]['fields']['path'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    } else if (edit_online.indexOf(results[i]['fields']['format']) > -1) {
                        s = s + '<td onclick="show_file(\''+ results[i]['fields']['file_id'] + '\',\'' + results[i]['fields']['format'] + '\')"><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    } else {
                        s = s + '<td><img src="static/img/' + all_icons[results[i]['fields']['format']] + '">' + results[i]['fields']['name'] + '</td>';
                    }
                    s = s + '<td>' + results[i]['fields']['times'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['total_times'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['create_time'].replace('T', ' ') + '</td>';
                    s = s + '<td style="white-space: normal;"><button class="actions" onclick="show_share_link(\'' + results[i]['pk'] + '\')">查看分享链接</button><button class="actions" onclick="copy_share_link(\'' + results[i]['pk'] + '\')">复制分享链接</button><button class="actions" onclick="delete_file(\'' + results[i]['pk'] + '\', 6)">删除</button></td></tr>';
                }
                document.getElementById("tbody").innerHTML = s;
                PagingManage($('#paging'), 1, 1, 'abc')
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}
function show_share_link(file_id) {
    let share_url = window.location.href + 'open/' + file_id;
    alert('分享链接为：' + share_url);
}
function copy_share_link(file_id) {
    let share_url = window.location.href + 'open/' + file_id;
    let aux = document.createElement('input');
    aux.setAttribute('value', share_url);
    document.body.appendChild(aux);
    aux.select();
    document.execCommand('copy');
    document.body.removeChild(aux);
    $.Toast('复制成功 ~', 'success');
}

function get_history(page) {
    document.getElementById("operation").innerHTML = operate_html;
    document.getElementById("layout-img").innerHTML = "";
    if (!page) {page=1;}
    $.ajax({
        type: "GET",
        url: "file/history?page=" + page,
        success: function (data) {
            if (data['code'] === 0) {
                document.getElementsByClassName("table_style")[0].innerHTML = '<th width="15%">文件ID</th><th width="30%">文件名称</th><th width="10%">操作类型</th><th width="15%">操作IP</th><th width="20">操作时间</th>';
                let s = "";
                let results = data['data']['data'];
                for (let i=0; i<results.length; i++) {
                    s = s + '<tr><td>' + results[i]['fields']['file_id'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['file_name'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['operate'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['ip'] + '</td>';
                    s = s + '<td>' + results[i]['fields']['operate_time'].replace('T', ' ') + '</td></tr>';
                }
                document.getElementById("tbody").innerHTML = s;
                PagingManage($('#paging'), data['data']['total_page'], data['data']['page'], 'get_history(')
            } else {
                $.Toast(data['msg'], 'error');
            }
        }
    })
}

function editor_online(file_id) {
    open_md(file_id);
}

function open_md(file_id) {
    document.getElementsByClassName("iframe_div")[0].style.display = 'block';
    document.getElementById("iframe_id").src = 'md/view?id=' + file_id;
    document.getElementById("close_iframe").onclick = function () {
        let content = document.getElementById("iframe_id").contentWindow.document.getElementById("editormd").getElementsByTagName("textarea")[0].value;
        let file_id = document.getElementById("iframe_id").contentWindow.document.getElementById("file_id").value;
        let content_len = document.getElementById("iframe_id").contentWindow.document.getElementById("file_id").name;
        if (parseInt(content_len) === content.length) {
            document.getElementById("iframe_id").src = '';
            document.getElementsByClassName("iframe_div")[0].style.display = 'none';
            return;
        }
        let post_data = {
            file_id: file_id,
            base64: btoa(unescape(encodeURIComponent(content)))
        }
        $.ajax({
            type: "POST",
            url: "md/edit",
            data: post_data,
            dataType: "json",
            success: function (data) {
                if (data['code'] === 0) {
                    $.Toast(data['msg'], 'success');
                    refresh_folder();
                } else {
                    $.Toast(data['msg'], 'error');
                    return;
                }
                document.getElementById("iframe_id").src = '';
                document.getElementsByClassName("iframe_div")[0].style.display = 'none';
            }
        })
    }
}

function beauty_size(size) {
    size = size / 1024;
    if (size < 1000) {
        return size.toFixed(2) + ' KB';
    } else {
        size = size / 1024;
    }
    if (size < 1000) {
        return size.toFixed(2) + ' MB';
    } else {
        return (size / 1024).toFixed(2) + ' GB';
    }
}
