const movies = [

{
title:"Avatar 2",
year:"2022",
rating:"8.5",
image:"https://image.tmdb.org/t/p/w500/t6HIqrRAclMCA60NsSmeqe9RmNV.jpg"
},

{
title:"John Wick",
year:"2023",
rating:"8.2",
image:"https://image.tmdb.org/t/p/w500/vZloFAK7NmvMGKE7VkF5UHaz0I.jpg"
},

{
title:"Stranger Things",
year:"2024",
rating:"8.7",
image:"https://image.tmdb.org/t/p/w500/x2LSRK2Cm7MZhjluni1msVJ3wDF.jpg"
}


];


const box=document.getElementById("movies");


function showMovies(list){

box.innerHTML="";


list.forEach(movie=>{


box.innerHTML += `

<div class="card">

<img src="${movie.image}">

<h3>${movie.title}</h3>

<p>📅 ${movie.year}</p>

<p>⭐ ${movie.rating}</p>

<button>
▶ Դիտել
</button>


</div>

`;


});


}


showMovies(movies);



document
.getElementById("search")
.addEventListener(
"input",
(e)=>{


let value=e.target.value.toLowerCase();


showMovies(
movies.filter(
m=>m.title.toLowerCase()
.includes(value)
)
);


});