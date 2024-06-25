
function hide_modal(id) {
    let modal = document.getElementById(id);
    let modal_backdrop = document.getElementsByClassName('modal-backdrop')[0];
    modal.classList.remove('show');
    modal_backdrop.classList.remove('show');
}
function edit() {
    let name_label = document.getElementById('name_label');
    let place_label = document.getElementById('place_label');
    let jointime_label = document.getElementById('jointime_label');
    let card_label = document.getElementById('card_label');
    name_label.classList = 'form-control border-black bg-white text-start';
    name_label.disabled = false;
    place_label.classList = 'form-control border-black bg-white text-start';
    place_label.disabled = false;
    jointime_label.classList = 'form-control border-black bg-white text-start';
    jointime_label.disabled = false;
    card_label.classList = 'form-control border-black bg-white text-start';
    card_label.disabled = false;
}

function save() {
    let name_label = document.getElementById('name_label');
    let place_label = document.getElementById('place_label');
    let jointime_label = document.getElementById('jointime_label');
    let card_label = document.getElementById('card_label');
    name_label.classList = 'form-control border-white bg-white text-start ';
    name_label.disabled = true;
    place_label.classList = 'form-control border-white bg-white text-start ';
    place_label.disabled = true;
    jointime_label.classList = 'form-control border-white bg-white text-start ';
    jointime_label.disabled = true;
    card_label.classList = 'form-control border-white bg-white text-start ';
    card_label.disabled = true;
    fetch('/api/manage?' + new URLSearchParams({ "name": name_label.value, 'place': place_label.value, 'jointime': jointime_label.value, 'cardid': card_label.value, 'key': '_id', 'value': window.location.href.split('/')[3].split('#')[0] }), { method: 'PUT' })
        .then(response => (load_data()))
}

//補打卡
async function make_up() {
    let time = new Array(3);
    time[0] = document.getElementById('modal_clockin_time').value;
    time[1] = document.getElementById('modal_workover_time').value;
    time[2] = document.getElementById('modal_clockout_time').value;
    let date_now = document.getElementById('modal_date').value;
    let value = document.getElementById('card_label').value;
    let types = ['clockin', 'workovertime', 'clockout'];

    console.log(time);
    for (let i in time) {
        if (time[i]) {
            time[i] = date_now + ' ' + time[i];
            time[i] += ':0';
        } else
            time[i] = '0:0:0';
    }
    hide_modal('exampleModal');
    for (let i in time) {
        if (time[i] != '0:0:0') {
            await fetch('/api/staff', { method: 'POST', body: "key=cardid&value=" + value + "&time=" + time[i] + '&type=' + types[i], headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
        }
    }
    load_data();
}

//補打卡
function delete_record() {
    let date_now = document.getElementById('modal_date_delete').value;
    let value = document.getElementById('card_label').value;
    hide_modal('delete_record_modal');
    fetch('/api/staff', { method: 'DELETE', body: "key=cardid&value=" + value + "&time=" + date_now, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
        .then(()=>{load_data()});
    

}