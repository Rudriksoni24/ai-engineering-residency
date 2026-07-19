const checks=document.querySelectorAll("input[type=checkbox]");

const progress=document.getElementById("overallProgress");

const progressText=document.getElementById("progressText");

const theme=document.getElementById("themeToggle");

load();

checks.forEach((box,index)=>{

box.addEventListener("change",()=>{

save();

update();

});

});

theme.onclick=()=>{

document.body.classList.toggle("light");

localStorage.setItem("theme",document.body.classList.contains("light"));

}

function update(){

let done=0;

checks.forEach(c=>{

if(c.checked) done++;

});

let percent=Math.round(done/checks.length*100);

progress.style.width=percent+"%";

progressText.innerHTML=percent+"%";

}

function save(){

let data=[];

checks.forEach(c=>data.push(c.checked));

localStorage.setItem("tasks",JSON.stringify(data));

}

function load(){

let tasks=JSON.parse(localStorage.getItem("tasks"));

if(tasks){

checks.forEach((c,i)=>c.checked=tasks[i]);

}

if(localStorage.getItem("theme")=="true"){

document.body.classList.add("light");

}

update();

}