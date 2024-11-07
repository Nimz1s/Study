const visible = document.getElementById('visible1');
const visible2 = document.getElementById('visible2');
const visible3 = document.getElementById('visible3');

function reviews(){
    visible.style.display = "flex";
    visible2.style.display = "none";
    visible3.style.display = "none";
}

function question(){
    visible.style.display = "none";
    visible2.style.display = "flex";
    visible3.style.display = "none";
}

function info(){
    visible.style.display = "none";
    visible2.style.display = "none";
    visible3.style.display = "flex";
}
