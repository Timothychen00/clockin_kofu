var menu_btn=document.getElementById('menu');
var dashboard=document.getElementById('dashboard');
menu_btn.addEventListener('click',(event)=>{
    if (String(dashboard.classList).includes('col-2')){
        dashboard.classList='col-1 px-lg-3';

        document.getElementById('word').style.display='none';
        document.getElementById('word-2').style.display='none';
        document.getElementById('word-3').style.display='none';
        
    }
    else{
        dashboard.classList='col-2 px-lg-3';
        document.getElementById('word').style.display='block';
        document.getElementById('word-2').style.display='block';
        document.getElementById('word-3').style.display='block';
    }
})