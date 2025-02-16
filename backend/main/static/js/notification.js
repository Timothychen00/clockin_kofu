function load_notification_class(classes){
    console.log('classes')
    let notification_class_box=document.getElementById('notification-class');
    notification_class_box.innerHTML='';
    for (let i of classes){
        console.log(i);
        notification_class_box.innerHTML+="<button class=\"badge pill-btn rounded-pill\">"+i+"</button>"
    }
//     <div class="col-2" id="notification-class">
//     <button class="badge pill-btn rounded-pill">Clockin</button>
//     <button class="badge pill-btn rounded-pill">Primary</button>
//     <button class="badge pill-btn rounded-pill">Primary</button>
//     <button class="badge pill-btn rounded-pill">Primary</button>
    
// </div>
}

function offsetDate(offset){
    date=document.getElementById('date');
    console.log('as date:',date.valueAsDate);
    if (!date.valueAsDate){
        currentDate=new Date()
    }else{
        currentDate=new Date(date.valueAsDate);
        currentDate.setDate(currentDate.getDate() + offset);
    }

    date.valueAsDate = currentDate;
    load_notification();
}

offsetDate()
function load_notification(){
    let date=document.getElementById('date').value;
    date= date.toLocaleString();
    console.log('date',date);

    fetch('/api/notifications?date='+date,{credentials: 'include'})
    .then((res)=>(res.json()))
    .then((res)=>{
        console.log(res);
        
        let classes =new Set();
        let notificationbox=document.getElementById('notification-box')
        notificationbox.innerHTML='';
        for(let i=0;i<res.length;i++){
            tags='';
            for (let j=0;j<res[i].tags.length;j++){
                classes.add(res[i].tags[j]);
                tags+="<span class=\"badge rounded-pill text-bg-primary\">"+res[i].tags[j]+"</span>";
            }
            notificationbox.innerHTML+="\
                            <div class=\"col-12 rounded border border-2 ps-4 py-2 d-flex flex-column mb-2\" >\
                            <div ><h5>"+res[i]['title']+"</h5></div>\
                            <div > "+tags+"</div>\
                            <div >"+res[i]['content']+"</div>\
                            <div class=\"d-inline-flex justify-content-between\">\
                                <div class=\"align-self-end flex-end\" >"+res[i]['publisher']+"</div>\
                                <div  class=\"bold\">"+res[i]['timestamp']+"</div>\
                            </div>\
                        </div>\
                        "
            
        }
        console.log(classes);
        load_notification_class(classes);
    })
}

// method: 'POST',
// body: JSON.stringify(data),
// headers: { 'content-type': 'application/json' },
// credentials: 'include'

function addNotificationTime(){
    if (document.getElementById('notification-time').childElementCount<3)
        document.getElementById('notification-time').innerHTML+="<input class='btn mx-2 border border-1' style='width:120px'  type=\'time\'/> ";
}

load_notification()