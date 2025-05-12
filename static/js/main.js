const menu = document.querySelector('.bars');
let menustate = false;
menu.addEventListener('click', showMenu);
function showMenu(){
    if(!menustate) {
        menu.classList.add('is-active');
        document.querySelector('.nav-links').classList.add('open');
        menustate = true;
    } else {
        menu.classList.remove('is-active');
        document.querySelector('.nav-links').classList.remove('open');
        menustate = false;
    }
}