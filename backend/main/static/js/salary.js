
function handle_mode(type){
    if (type=='data'){
        document.getElementById('data').classList.remove('visually-hidden');
        document.getElementById('calculate').classList.add('visually-hidden');
        document.getElementById('contact').classList.add('visually-hidden');
    }else if(type=='calculate'){
        document.getElementById('calculate').classList.remove('visually-hidden');
        document.getElementById('data').classList.add('visually-hidden');
        document.getElementById('contact').classList.add('visually-hidden');
    }else{
        document.getElementById('contact').classList.remove('visually-hidden');
        document.getElementById('calculate').classList.add('visually-hidden');
        document.getElementById('data').classList.add('visually-hidden');
    }  
}
function salary(){
    const button=document.getElementById('salary');
    if(button.classList.contains('active')){//turn off
        button.classList.remove('active');
        button.blur();
        document.getElementById('salary_title').remove();
        month_type=document.getElementById('last').classList.contains('active')?month_type='last':month_type='this';
        console.log('here',month_type);
        load_data(month_type=month_type);
    }else{
        button.classList.add('active');
        delete_title=document.getElementById('delete_title');
        salary_title=document.createElement('th');
        salary_title.innerText='預估薪資';
        salary_title.setAttribute('scope', 'col');
        salary_title.setAttribute('style', 'min-height:100px!important;');
        salary_title.setAttribute('id', 'salary_title');
        delete_title.before(salary_title)
        month_type=document.getElementById('last').classList.contains('active')?month_type='last':month_type='this';
        console.log('here',month_type);
        load_data(month_type=month_type);

    }
}
function setting(){
    const button=document.getElementById('setting_button');
    const setting_icon=document.getElementById('setting_icon');
    if(button.classList.contains('active')){//turn off
        button.classList.remove('active');
        setting_icon.classList.add('element-rotate');

        button.blur();
    }else{
        button.classList.add('active');
        setting_icon.classList.remove('element-rotate');

    }

}

function salary_save(){
    const unitpay=document.getElementById('unitpay');
    const duration=document.getElementById('duration');
    const bias=document.getElementById('bias');

    fetch('/api/settings?' + new URLSearchParams({ "unitpay": unitpay.value, 'duration': duration.value, 'bias': bias.value}), { method: 'PUT' })
        .then(response => (load_data()))
    let modalEl = document.getElementById('exampleModalsalary');
	let mymodal = bootstrap.Modal.getInstance(modalEl);
	mymodal.hide();
    load_data(show_salary='true');
}


