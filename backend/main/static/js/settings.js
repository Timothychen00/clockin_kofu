const { elements } = require("chart.js");

function acitve_tooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function settings_init() {
    const button = document.getElementById('countdown-btn');
    const tokenContainer = document.getElementById('tokenContainer');
    let countdownInterval;

    // 當按鈕被點擊時
    button.addEventListener('click', async function () {
        // 如果按鈕已經被禁用，直接回傳不執行
        console.log('pressed')
        if (button.disabled) return;

        // 生成一個 token
        const token = await generate_token();
        tokenContainer.innerHTML = '';
        const tokenBlock = document.createElement('div');
        tokenBlock.className = 'token-block pt-2 px-2 pe-4';
        tokenBlock.textContent = token;
        tokenBlock.setAttribute("data-bs-toggle", "tooltip");
        tokenBlock.setAttribute("data-bs-placement", "top");
        tokenBlock.setAttribute("data-bs-title", "將token傳送給line官方帳號完成綁定（有效時間5分鐘）");

        // 當使用者點 token 區塊時，複製 token 到剪貼簿
        tokenContainer.addEventListener('click', function () {
            navigator.clipboard.writeText('bind-' + token).then(() => {
                alert('Token 已複製到剪貼簿！');
            }).catch(() => {
                alert('複製失敗！');
            });
        });
        tokenContainer.appendChild(tokenBlock);
        tokenContainer.innerHTML += "<ion-icon name=\"clipboard\" style='margin-left:-25px;margin-top:13px;'></ion-icon>";
        acitve_tooltips()//啟動bootstrap的tooltips功能

        // 禁用按鈕，並開始 60 秒倒計時
        let timeLeft = 60;
        button.disabled = true;
        button.textContent = `${timeLeft} s`;

        countdownInterval = setInterval(() => {
            timeLeft--;
            if (timeLeft > 0) {
                button.textContent = `${timeLeft} s`;
            } else {
                clearInterval(countdownInterval);
                button.disabled = false;
                button.textContent = '立即綁定';
            }
        }, 1000); // 1000 毫秒等於 1 秒

    });
}

function load_settings() {
    console.log('[load_settings]')
    fetch('/api/settings', { credentials: 'include' })
        .then((res) => (res.json()))
        .then((res) => {
            let settings_unitpay_element = document.getElementById('settings_unitpay_element');
            let settings_bias_element = document.getElementById('settings_bias_element');
            let settings_duration_element = document.getElementById('settings_duration_element');
            let settings_bind_box = document.getElementById('settings_bind_box');
            let notification_time_element = document.getElementById('notification-time');

            console.log(res);
            settings_unitpay_element.value = res['data']['unitpay']
            settings_bias_element.value = res['data']['bias']
            settings_duration_element.value = res['data']['duration']

            console.log(res['data']['notification-time']);
            for (let ele of res['data']['notification-time']) {
                addNotificationTime(ele);
            }


            if (res['data']['notification-status'] == 'None') {
                settings_bind_box.innerHTML = "\<button class='btn border' id=\"countdown-btn\">立即綁定</button><div id=\"tokenContainer\"  class='d-inline-flex'></div>"
                settings_init();
            } else {
                settings_bind_box.innerHTML = "\<button class='btn'>已綁定</button><ion-icon name=\"close-circle\" class='animation-scale' style='color:red' onclick='unbind()'></ion-icon>"
            }

        })
}

function save_settings() {
    console.log('[save_settings]')
    let settings_unitpay = document.getElementById('settings_unitpay_element').value;
    let settings_bias = document.getElementById('settings_bias_element').value;
    let settings_duration = document.getElementById('settings_duration_element').value;
    let notification_time_element = document.getElementById('notification-time');

    let notification_time = new Array();

    for (let element of notification_time_element.children) {
        if (element.value) {
            notification_time.push(element.value)
            console.log(element.value);
        }
    }
    //update
    fetch('/api/settings?' + new URLSearchParams({
        "unitpay": settings_unitpay,
        'duration': settings_duration,
        'bias': settings_bias,
        'notification-time':notification_time
    }), { method: 'PUT', credentials: 'include' })
        .then(response => (response.json()))
        .then((res)=>{
            console.log(res);
        })


}

function unbind() {
    console.log('[unbind]')
    fetch('/api/notifications?unbindAll=1', { method: "delete", credentials: 'include' })
        .then((res) => (res.json()))
        .then((res) => {
            console.log(res)
            load_settings()
        })
}
async function generate_token() {
    console.log('[generate_token]')

    let response = await fetch('/api/settings?key=token', { credentials: 'include' })
    let res = await response.json()
    console.log(res)
    return res['token']
}

