
function hide_modal(id) {
    let modal = document.getElementById(id);
    let modal_backdrop = document.getElementsByClassName('modal-backdrop')[0];
    modal.classList.remove('show');
    modal_backdrop.classList.remove('show');
}


function load_data(month_type = 'this') {
    let date = new Date();

    let month = '';
    if (month_type == 'this') {
        month = Number(date.getFullYear()) + "-" + String(date.getMonth() + 1).padStart(2, '0');
        document.getElementById('this').classList.add('active');
        document.getElementById('last').classList.remove('active');
    } else {
        if (date.getMonth() == 0)
            month = Number(date.getFullYear() - 1) + "-" + 12;
        else
            month = Number(date.getFullYear()) + "-" + String(date.getMonth()).padStart(2, '0');
        document.getElementById('last').classList.add('active');
        document.getElementById('this').classList.remove('active');
    }
    
    const para_obj={
        'key': '_id', 'value': window.location.href.split('/')[window.location.href.split('/').length-1].split('#')[0] 
    }
    if(window.location.href.includes("preview")){
        para_obj.key='hash_id';
    } 
    console.log("para_obj",para_obj);

    fetch("/api/manage?" + new URLSearchParams(para_obj), { method: 'GET' })
        .then(res => (res.json()))
        .then((res) => {
            console.log(res);
            let name_label = document.getElementById('name_label');
            name_label.value = res[0]['name'];
            let place_label = document.getElementById('place_label');
            place_label.value = res[0]['place'];
            let jointime_label = document.getElementById('jointime_label');
            jointime_label.value = res[0]['jointime'];
            let card_label = document.getElementById('card_label');
            card_label.value = res[0]['cardid'];

            let preview_link=document.getElementById('preview-hash');
            preview_link.href+= res[0]['hash_id'];

            // //補打卡重置
            if (para_obj.key!="hash_id"){
                document.getElementById('modal_clockin_time').value = '';
                document.getElementById('modal_workover_time').value = '';
                document.getElementById('modal_clockout_time').value = '';
            }
            console.log(res[0]["log"][month]);
            let keys = '';
            console.log(month);
            if (month in res[0]['log'])
                keys = Object.keys(res[0]["log"][month]);
            console.log(keys);
            currentmonth_log.innerHTML = '';
            let res_length = keys.length;
            if (res_length > 0) {
                let logs = res[0]['log'][month];

                let currentmonth_log = document.getElementById('currentmonth_log');
                let workday = document.getElementById('workday');
                let worktime = res[0]['work'][month];
                let workovertime = res[0]['workover'][month];
                let worktime_label = document.getElementById('worktime_label');
                let workovertime_label = document.getElementById('workovertime_label');
                worktime_label.innerText = worktime[0] + ' hr  ' + worktime[1] + ' m';
                workovertime_label.innerText = workovertime[0] + ' hr  ' + workovertime[1] + ' m';
                workday.innerText = res_length + ' 天';

                let total_time = worktime[0] * 60 + worktime[1] + workovertime[0] * 60 + workovertime[1];
                let time_per = total_time / res_length;

                let time_per_label = document.getElementById('time_per_label');
                time_per_label.innerText = Math.floor(time_per / 60) + ' hr ' + Math.floor(time_per % 60) + ' m';
                //generating html 
                for (let log = 0; log < res_length; log++) {

                    currentmonth_log.innerHTML += '\
                <tr style="height:20px" class="align-text-top">\
                <td>'+ keys[log] + '</td><td>' + logs[keys[log]]['clockin'] + '</td><td>' + logs[keys[log]]['workovertime'] + '</td><td>' + logs[keys[log]]['clockout'] + '</td><td>' + logs[keys[log]]['duration'][0][0] + ' hr ' + logs[keys[log]]['duration'][0][1] + ' m</td><td>' + logs[keys[log]]['duration'][1][0] + ' hr ' + logs[keys[log]]['duration'][1][1] + ' m</td></tr>\
                </tr>';
                }
            }
        });
}

window.onload = load_data();
