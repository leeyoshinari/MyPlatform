document.getElementById("wrap").onkeyup = function (event) {
        if (event.keyCode === 13) {
            change_pwd();
        }
};

$("#submit_b").click(function () {
    change_pwd();
});


function change_pwd() {
    let username = document.getElementById('username').value;
    let old_p = document.getElementById('password').value;
    let new_p = document.getElementById('password1').value;
    let new_p1 = document.getElementById('password2').value;
    if (username === '' || old_p === '' || new_p === '') {
        $.Toast('username or password is not blank  ~', 'error');
        return;
    }
    if (new_p !== new_p1) {
        $.Toast('Two new passwords are different ~', 'error');
        return;
    }
    if (old_p === new_p) {
        $.Toast('Old password is same as new password ~', 'error');
        return;
    }
    let c = new Date().getTime().toString();
    let postdata = {
        'username': username,
        'old_password': parse_pwd(old_p, c),
        'new_password': parse_pwd(new_p, c),
        'current_time': c
    };
    $.ajax({
        type: 'post',
        url: 'changePwd',
        data: postdata,
        datatype: 'json',
        success: function (data) {
            if (data['code'] === 0) {
                $.Toast(data['msg'], 'success');
                window.location.href = 'login';
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

