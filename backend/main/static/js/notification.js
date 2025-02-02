function load_notification(){
    fetch('/api/notifications?tags=clockin',{credentials: 'include'})
    .then((res)=>(res.json()))
    .then((res)=>{
        console.log(res);
        notificationbox=document.getElementById('notification-box')
        for(let i=0;i<res.length;i++){
            tags='';
            for (let j=0;j<res[i].tags.length;j++){
                tags+="<span class=\"badge rounded-pill text-bg-primary\">"+res[i].tags[j]+"</span>";
            }
            notificationbox.innerHTML+="\
                            <div class=\"col-12 rounded border border-1 ps-4 py-2 d-flex flex-column \" >\
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
    })
}

// method: 'POST',
// body: JSON.stringify(data),
// headers: { 'content-type': 'application/json' },
// credentials: 'include'
load_notification()