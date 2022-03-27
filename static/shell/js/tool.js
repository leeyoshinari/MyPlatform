$(document).unbind('keydown').bind('keydown', function (e) {
    console.log(e.keyCode);
    if (e.keyCode === 17 && e.keyCode === 86) {
        console.log('paste');
    }
});

document.onclick = function () {
    if (window.getSelection) {
        document.execCommand('Copy');
    }
};
