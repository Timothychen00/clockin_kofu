
function load_data(month_type='this') {
	fetch('/api/manage', { method: "GET",mode: 'no-cors' })
		.then((response) => {
			// 這裡會得到一個 ReadableStream 的物件
			// console.log(response);
			return response.json();// 可以透過 blob(), json(), text() 轉成可用的資訊
		}).then((jsonData) => (inject_html(jsonData,month_type)))//講資料植入html
		.catch((err) => {
			console.log('錯誤:', err);
		});
}
window.onload = load_data();

function delete_user(id) {
	fetch('/api/manage', { method: 'DELETE', body: "key=_id&value=" + id, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
		.then(() => { let users = document.getElementById('users'); users.innerHTML = ''; load_data() });
	let modalEl = document.getElementById('exampleModal' + id);
	let mymodal = bootstrap.Modal.getInstance(modalEl);
	mymodal.hide();
}

function insert_user() {
	fetch('/api/manage', { method: 'POST', body: 'name=' + document.getElementById('name').value + '&place=' + document.getElementById('place').value+'&jointime=' + document.getElementById('jointime').value + '&cardid=' + document.getElementById('cardid').value, headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
		.then(() => { let users = document.getElementById('users'); users.innerHTML = ''; load_data() });

}

function search() {
	key = document.getElementById('key').value;
	value = document.getElementById('value').value;
	fetch('api/manage?' + new URLSearchParams({ 'key': key, 'value': value }), {})
		.then((response) => (response.json()))
		.then(res => (inject_html(res)))
}

function inject_html(data,month_type='this') {
	let users = document.getElementById('users');
	let date = new Date();
	users.innerHTML = '';

    var month = '';
    if (month_type == 'this') {
        month = date.getFullYear() + "-" + (Number(date.getMonth()) + 1);
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
	console.log(month);


	for (let i = 0; i < data.length; i++) {
		work = [0, 0];
		workover = [0, 0];
		// console.log(month in data[i].work);
		if (month in data[i].work) {
			work = data[i]['work'][month];
			workover = data[i]['workover'][month];
		}
		console.log(data[i].length)
		// work=jsonData[i].work;
		users.innerHTML += "<tr><td>" + data[i]['_id'] + "</td><td><a href='/" + data[i]['_id'] + "'>" + data[i]["name"] + "</a></td><td>" + data[i]["place"] + "</td><td>" + work[0] + "  hr  " + work[1] + " m  " + "</td><td>" + workover[0] + "  hr  " + workover[1] + " m" + '</td>\
		<td>\
		<button type="button" class="btn btn-danger" data-bs-toggle="modal"\
			data-bs-target="#exampleModal'+ data[i]['_id'] + '">刪除</button>\
		<div class="modal fade" id="exampleModal'+ data[i]['_id'] + '" tabindex="-1"\
			aria-labelledby="exampleModalLabel" aria-hidden="true">\
			<div class="modal-dialog">\
				<div class="modal-content">\
					<div class="modal-header">\
						<h5 class="modal-title" id="exampleModalLabel">確認刪除？</h5>\
						<button type="button" class="btn-close" data-bs-dismiss="modal"\
							aria-label="Close"></button>\
					</div>\
					<div class="modal-body">\
						<p class="fw-bold">請注意！刪除後將無法復原！</p>\
					</div>\
					<div class="modal-footer">\
						<button type="button" class="btn btn-secondary"\
							data-bs-dismiss="modal">取消</button>\
						<button type="button" class="btn btn-danger"\
							onclick="delete_user('+ data[i]['_id'] + ')" >確認刪除</button>\
					</div>\
				</div>\
			</div>\
		</div>\
		</td></tr>';
	}
}