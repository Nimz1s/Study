const visiblepr = document.getElementById('visibleproducts');
const visibleadd = document.getElementById('visibleaddproducts');


function product(){
    visiblepr.style.display = "flex";
    visibleadd.style.display = "none";
}

function addproduct(){
    visiblepr.style.display = "none";
    visibleadd.style.display = "flex";
}



