let menuicn = document.querySelector(".menuicn");
let nav = document.querySelector(".navcontainer");

menuicn.addEventListener("click", () => {
    nav.classList.toggle("navclose");
})
/* Sidebar Navigation */
document.getElementById('product_image').addEventListener('change', function() {
    var fileName = this.files[0] ? this.files[0].name : 'Choose Image';
    this.nextElementSibling.innerText = fileName; // Update label text
});