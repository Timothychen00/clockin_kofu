function a(b){
    console.log(b);
    if(b())
        console.log(666);
}
let c=3;
let d=4;

a(()=>(c>d));