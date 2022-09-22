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
    let to_url = document.getElementById('location').value;
    if (username === '' || p === '') {
        $.Toast('username or password is not blank  ~', 'error');
        return;
    }
    let c = new Date().getTime().toString();
    let postdata = {
        'username': username,
        'password': parse_pwd(p, c),
        'currentTime': c
    };
    $.ajax({
        type: 'post',
        url: 'login',
        data: postdata,
        datatype: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = to_url;
            } else {
                $.Toast(data['msg'], 'error');
            }
        },
    });
}

function parse_pwd(p, s) {
    let a = '';
    let total = s.length;
    for (let i = 0; i < p.length; i++) {
        if (i >= total) {
            a += String.fromCharCode(p[i].charCodeAt() ^ parseInt(s[i - total]));
        } else {
            a += String.fromCharCode(p[i].charCodeAt() ^ parseInt(s[i]));
        }
    }
    return a
}

