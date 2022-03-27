let testEditor = editormd("editormd", {
        width  : "95%",
        height : 720,
        path   : '../static/editor.md/lib/',
        toolbar_autofixed: true,
        codeFold: true,
        searchReplace: true,
        emoji: true,
        sequenceDiagram: true,
        taskList: true,
        tocm: true,
        // tex: true,
        flowChart: true,
        htmlDecode: "style,script,iframe",
        saveHTMLToTextarea: true,
        imageUpload: true,
        imageFormats: ["jpg", "jpeg", "png", "bmp", "gif"],
    });

let init_len = document.getElementById("editormd").getElementsByTagName("textarea")[0].value.length;
document.getElementById("file_id").name = init_len;
window.setInterval(function () {
            get_textarea_text();
    }, 30000
)

function get_textarea_text() {
        let editor = document.getElementById("editormd").getElementsByTagName("textarea")[0].value;
        if (editor.length !== init_len) {
                save();
                init_len = editor.length;
                document.getElementById("file_id").name = init_len;
        }
}

function save() {
        let content = document.getElementById("editormd").getElementsByTagName("textarea")[0].value;
        let file_id = document.getElementById("file_id").value;
        let post_data = {
                file_id: file_id,
                base64: btoa(unescape(encodeURIComponent(content)))
        }
        $.ajax({
                type: "POST",
                url: "edit",
                data: post_data,
                dataType: "json",
                success: function (data) {
                        if (data['code'] === 1) {
                                $.Toast(data['msg'], 'error');
                                return;
                        }
                }
        })
}