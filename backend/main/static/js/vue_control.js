
const app = Vue.createApp({
    data: () => {
        return { message: 'Hello Vue!' }
    },
    methods: {
        calculate() {
            array_places=new Array();




            places = document.getElementsByClassName('place')
            // places.forEach(element => {
            //     if (!array_places.includes(element)){
            //         array_places.push(element);
            //     }
            // });
            console.log(333333);
            console.log(places)
        },

    },
    beforeMount() {
        this.calculate()
    },


})
app.mount('#app')
