

document.addEventListener('DOMContentLoaded', function() {
    // When the user scrolls the page, execute myFunction
    window.addEventListener('scroll', myFunction);

    myFunction();
    //window.onscroll = function() {myFunction()};

    // Add the sticky class to the navbar when you reach its scroll position. Remove "sticky" when you leave the scroll position
    function myFunction() {
        // Get the navbar
        const top_bar = document.getElementById("top-navbar");
        const middle_bar = document.getElementById("middle_bar");
        const main_section = document.getElementById("main_section");
        const myCarousel = document.getElementById("carousel");

        if (middle_bar) {
        // Get the offset position of the navbar
            if (window.pageYOffset > myCarousel.clientHeight) {
            //        snap_mode = true;

            //        middle_bar.classList.add("stickyMiddle")
                    middle_bar.style.top = top_bar.offsetTop + "px";
            middle_bar.style.position = "fixed";
            //        middle_bar.style.zIndex = "100";
            //        main_section.style.marginTop = "5px";

            //        main_section.style.position = "fixed"
            } else {
            //        snap_mode = false;
            //        middle_bar.classList.remove("stickyMiddle");
            //        middle_bar.style.top = top_bar.offsetTop + "px";
                    middle_bar.style.top = top_bar.offsetTop + myCarousel.clientHeight + "px";

            middle_bar.style.position = "absolute";
            //        main_section.style.marginTop = "0px";
            //        main_section.style.paddingTop = "0px";
            //        main_section.style.position = "unset"
            }
        }

    }
});
