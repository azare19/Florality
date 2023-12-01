// FILE FOR home2.html
// Get Started 

// when document is ready
$(function() {

    // event handler on get started button
    $("#get_started").click(function(){    
        start_flow();
    })
});

// get started
function start_flow(){
    window.location.href = "/bouquet";
}