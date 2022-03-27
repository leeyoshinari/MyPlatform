document.getElementById("wrap").onkeyup = function (event) {
        if (event.keyCode === 13) {
            login();
        }
};

$("#login_b").click(function () {
    login();
});


function login() {
    let username = document.getElementById('username').value;
    let p = document.getElementById('password').value;
    if (username === '' || p === '') {
        $.Toast('用户名和密码不能为空！', 'error');
        return;
    }
    let c = new Date().getTime().toString();
    let total = c.length;
    let password = '';
    for (let i = 0; i < p.length; i++) {
        if (i >= total) {
            password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(c[i - total]));
        } else {
            password += String.fromCharCode(p[i].charCodeAt() ^ parseInt(c[i]));
        }
    }
    let postdata = {
        'username': username,
        'password': password,
        'currentTime': parseInt(c)
    };
    $.ajax({
        type: 'post',
        url: 'login',
        data: postdata,
        datatype: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                let currnt_url = window.location.href;
                window.location.href = currnt_url.substring(0, currnt_url.length-5);
            } else {
                $.Toast(data['msg'], 'error');
            }
        },
    });
}
