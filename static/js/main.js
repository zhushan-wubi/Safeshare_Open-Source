window.addEventListener("wheel",(e)=>{

    if(e.deltaY > 0){

        window.scrollTo({
            top:window.innerHeight,
            behavior:"smooth"
        });

    }else{

        window.scrollTo({
            top:0,
            behavior:"smooth"
        });

    }

});
