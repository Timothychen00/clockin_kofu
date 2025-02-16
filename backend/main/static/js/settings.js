function load_settings() {
    console.log('[load_settings]')
    fetch('/api/settings', { credentials: 'include' })
        .then((res) => (res.json()))
        .then((res) => {
            let settings_unitpay_element=document.getElementById('settings_unitpay_element');
            let settings_bias_element=document.getElementById('settings_bias_element');
            let settings_duration_element=document.getElementById('settings_duration_element');
            let settings_bind_box=document.getElementById('settings_bind_box');

            console.log(res);
            settings_unitpay_element.value=res['data']['unitpay']
            settings_bias_element.value=res['data']['bias']
            settings_duration_element.value=res['data']['duration']

            if (res['data']['notification-status']=='None'){
                settings_bind_box.innerHTML="\<button class='btn' onclick='generate_binding()'>立即綁定</button>"
            }else{
                settings_bind_box.innerHTML="\<button class='btn'>已綁定</button><ion-icon name=\"close-circle\" class='animation-scale' style='color:red' onclick='unbind()'></ion-icon>"
            }

        })
}
function save_settings() {
    console.log('[save_settings]')
}
function unbind(){
    console.log('[unbind]')
    fetch('/api/settings?unbindAll=1', {method:"delete", credentials: 'include' })
    .then((res) => (res.json()))
        .then((res) => {
            console.log(res)
            load_settings()
        })
}
function generate_binding(){
    if (window.token_block==false || window.token_block==undefined){
        console.log('[generate_binding]')

        fetch('/api/settings?key=token', { credentials: 'include' })
            .then((res) => (res.json()))
            .then((res) => {

                console.log(res);
                window.token_block=true
                setTimeout(()=>{
                    window.token_block=false
                },60000)


            })
    }else{
        alert('retry after 60s')
    }
}
