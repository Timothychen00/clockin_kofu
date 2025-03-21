
function handle_mode(type){
    if (type=='people'){
        document.getElementById('people').classList.remove('visually-hidden');
        document.getElementById('people').classList.add('animation-floating');
        document.getElementById('notifications').classList.add('visually-hidden');
        document.getElementById('settings').classList.add('visually-hidden');
        document.getElementById('contact').classList.add('visually-hidden');

        document.getElementById('notifications').classList.remove('animation-floating');
        document.getElementById('settings').classList.remove('animation-floating');
        document.getElementById('contact').classList.remove('animation-floating');

    }else if(type=='notifications'){
        load_notification()
        document.getElementById('notifications').classList.remove('visually-hidden');
        document.getElementById('notifications').classList.add('animation-floating');
        document.getElementById('people').classList.add('visually-hidden');
        document.getElementById('settings').classList.add('visually-hidden');
        document.getElementById('contact').classList.add('visually-hidden');

        document.getElementById('people').classList.remove('animation-floating');
        document.getElementById('settings').classList.remove('animation-floating');
        document.getElementById('contact').classList.remove('animation-floating');
    }else if (type=='contact'){
        document.getElementById('contact').classList.remove('visually-hidden');
        document.getElementById('contact').classList.add('animation-floating');
        document.getElementById('notifications').classList.add('visually-hidden');
        document.getElementById('settings').classList.add('visually-hidden');
        document.getElementById('people').classList.add('visually-hidden');

        document.getElementById('people').classList.remove('animation-floating');
        document.getElementById('settings').classList.remove('animation-floating');
        document.getElementById('notifications').classList.remove('animation-floating');
    }  
    else if (type=='settings'){
        load_settings()
        document.getElementById('settings').classList.remove('visually-hidden');
        document.getElementById('settings').classList.add('animation-floating');
        document.getElementById('notifications').classList.add('visually-hidden');
        document.getElementById('contact').classList.add('visually-hidden');
        document.getElementById('people').classList.add('visually-hidden');

        document.getElementById('notifications').classList.remove('animation-floating');
        document.getElementById('people').classList.remove('animation-floating');
        document.getElementById('contact').classList.remove('animation-floating');
    }  
}
function salary(){
    const button=document.getElementById('salary');
    if(button.classList.contains('active')){//turn off
        button.classList.remove('active');
        button.blur();
        document.getElementById('salary_title').remove();
        let month_type=document.getElementById('last').classList.contains('active')?'last':'this';
        console.log('here',month_type);
        load_data(month_type=month_type);
    }else{
        button.classList.add('active');
        const delete_title=document.getElementById('delete_title');
        const salary_title=document.createElement('th');
        salary_title.innerText='預估薪資';
        salary_title.setAttribute('scope', 'col');
        salary_title.setAttribute('style', 'min-height:100px!important;');
        salary_title.setAttribute('id', 'salary_title');
        delete_title.before(salary_title)
        let month_type=document.getElementById('last').classList.contains('active')?'last':'this';
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
    const modalEl = document.getElementById('exampleModalsalary');
	const mymodal = bootstrap.Modal.getInstance(modalEl);
	mymodal.hide();
    load_data(show_salary='true');
}


