

window.onload = function() {

    // Get the navbar
    var middle_bar = document.getElementById("middle_bar");
    var top_bar = document.getElementById("top-navbar");
    // When the user scrolls the page, execute myFunction
    window.addEventListener('scroll', myFunction);

    myFunction();
    var bar_position = middle_bar.offsetTop;


    // Add the sticky class to the navbar when you reach its scroll position. Remove "sticky" when you leave the scroll position
    function myFunction() {
        // Get the offset position of the navbar
        if (top_bar) {
            if (window.pageYOffset > bar_position - top_bar.clientHeight) {
                middle_bar.style.top = top_bar.offsetTop + "px";
                middle_bar.style.position = "fixed";
            } else {
                middle_bar.style.top = bar_position + "px";
                middle_bar.style.position = "absolute";
            }
        }

    }
};
