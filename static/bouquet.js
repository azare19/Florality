$(function() {
    toggle_visibility(1);

    $("#return_options_btn").click(function() {
        toggle_visibility(1);
    })

    $("#return_flower_shop_btn").click(function() {
        toggle_visibility(2);
    })

    $("#restart_btn").click(function() {
        window.location.href = "/bouquet"
    })

    $("#submit_btn").click(function(){
        let checkboxes = document.querySelectorAll('input[name="color_options"]:checked');
        let colors = [];
        checkboxes.forEach((checkbox) => {
            colors.push(checkbox.value);
        });

        let shape = document.querySelector('input[name="shape"]:checked');
        let vibe = document.querySelector('input[name="vibe"]:checked');
        let season = document.querySelector('input[name="season"]:checked');
        let extras = document.getElementById('extras');

        if (colors.length > 0 && shape && vibe && season) {
            $("#options_warning").addClass("hidden");
            submit_form(colors, shape.value, vibe.value, season.value, extras.value)
        }
        else {
            $("#options_warning").removeClass("hidden");
        }
    });

    $("#save_btn").click(function() {
        let selectedFlowersWithColors = [];

        let generationURL = $('.gen-img img').attr('src');
        console.log('save button clicked')
        console.log(generationURL)

        $('input[name="selected_flowers"]:checked').each(function () {
            let flowerName = $(this).val();

            let selectedColor = $(this).closest('.flower-option').find('select[name="flower_colors"]').val();

            selectedFlowersWithColors.push({flower: flowerName, color: selectedColor});
        })

        save_img(selectedFlowersWithColors, form_data, generationURL);
        req_img(selectedFlowersWithColors, form_data);
    }) 

    $("#x_btn").click(function() {
        let selectedFlowersWithColors = [];

        // Iterate over each selected flower
        $('input[name="selected_flowers"]:checked').each(function () {
            let flowerName = $(this).val();

            // Find the corresponding color for the selected flower
            let selectedColor = $(this).closest('.flower-option').find('select[name="flower_colors"]').val();

            // Append the flower name and selected color to the array
            selectedFlowersWithColors.push({ flower: flowerName, color: selectedColor });
        });

        req_img(selectedFlowersWithColors, form_data);
    })

    $("#img_btn").click(function () {
        // Implement the logic to visualize the bouquet when the button is clicked
        // You can call the function or make another AJAX request here
        let selectedFlowersWithColors = [];

        // Iterate over each selected flower
        $('input[name="selected_flowers"]:checked').each(function () {
            let flowerName = $(this).val();

            // Find the corresponding color for the selected flower
            let selectedColor = $(this).closest('.flower-option').find('select[name="flower_colors"]').val();

            // Append the flower name and selected color to the array
            selectedFlowersWithColors.push({ flower: flowerName, color: selectedColor });
        });

        // Log or use the selected flowers with colors as needed
        console.log("img_btn clicked");
        console.log(selectedFlowersWithColors);

        if (selectedFlowersWithColors.length > 0) {
            $("#flowers_warning").addClass("hidden");
            req_img(selectedFlowersWithColors, form_data)
        } else {
            $("#flowers_warning").removeClass("hidden");
        }
    });

    $('.option').click(function(){
        let checkboxes = document.querySelectorAll('input[name="color_options"]:checked');
        let shape = document.querySelectorAll('input[name="shape"]:checked');
        let vibe = document.querySelectorAll('input[name="vibe"]:checked');
        let season = document.querySelectorAll('input[name="season"]:checked');

        console.log("option clicked")

        if (checkboxes.length > 0) {
            $("#colors_step").addClass('done')
        } else {
            $("#colors_step").removeClass('done')
        }

        if (shape.length > 0) {
            $("#shape_step").addClass('done')
        } else {
            $("#shape_step").removeClass('done')
        }

        if (vibe.length > 0) {
            $("#vibe_step").addClass('done')
        } else {
            $("#vibe_step").removeClass('done')
        }

        if (season.length > 0) {
            $("#season_step").addClass('done')
        } else {
            $("#season_step").removeClass('done')
        }
    })
});

function submit_form(colors, shape, vibe, season, extras){
    let data = {"colors":colors,"shape":shape, "season":season, 'vibe':vibe, "extras":extras}
    $.ajax({
        type: "POST",
        url: "/submit_form",                
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        
        data : JSON.stringify(data),
        beforeSend: function () { 
            $("#spinner-div").show()
        },
        success: function(data, text){
            console.log("/submit_form success")     
            form_data = data
            show_results(data)
        },
        error: function(request, status, error){
            console.log("/submit_form error");
            console.log(request)
            console.log(status)
            console.log(error)
        },
        complete: function () { 
            $("#spinner-div").hide()
        },
    }); 
}

function show_results(data){
    toggle_visibility(2);

    console.log("Showing flower shop")

    if (data && data.flowers && data.flowers.length > 0) {
        var flowerContainer = $("<div class='flower-options'></div>");

        console.log("Flower images:")
        console.log(data.flower_images)

        console.log("Flowers list:")
        console.log(data.flowers)

        var index = 0;

        data.flowers.forEach(function (flower) {
            index += 1;
            var flowerId = flower + (index).toString();
            
            if (data.flower_colors[flower] != undefined) {
                var flowerDiv = $("<div class='flower-option'></div>");
                var checkbox = $("<input id='" + flowerId + "' class='checkbox' type='checkbox' name='selected_flowers' value='" + flower + "'> " + flower);
                
                var label = $("<label class='tooltip-custom' for='" + flowerId + "'><span class='tooltiptext flower-info'>" + data.flower_info[flower] + "</span></label>")
                var flowerImage = $("<img src='" + data.flower_images[flower] + "' alt='" + flower + "'>");
                var caption = $("<div class='flower-name'>" + flower + "</div>");
                
                // Create a select element for flower colors
                var flowerColorsSelect = $("<select class='colors-dropdown' name='flower_colors'></select>");

                // Iterate over each color for the current flower and create an option element
                data.flower_colors[flower].forEach(function (color) {
                    var colorOption = $("<option value='" + color + "'>" + color + "</option>");
                    flowerColorsSelect.append(colorOption);
                });
                // Append the image and checkbox to the container
                flowerDiv.append(flowerImage);
                flowerDiv.append(flowerColorsSelect);
                flowerDiv.append(caption);
                flowerDiv.append(checkbox);      
                flowerDiv.append(label);
    
                // Append the container to the flower options
                flowerContainer.append(flowerDiv);
            } else {
                console.log("Wrongly formatted flower colors")
            }
                
        });
        
        $("#results").prepend(flowerContainer);
    }
}

function req_img(selected_flowers, form_data){
    let data = {"selected_flowers":selected_flowers,"form_data":form_data}
    console.log("Requesting new bouquet image");
    console.log(data)

    $.ajax({
        type: "POST",
        url: "/req_img",                
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        
        data : JSON.stringify(data),
        beforeSend: function () { 
            $("#spinner-div").show()
        },
        success: function(data){
            console.log("/req_img successful")           
            new_form_data = data
            show_generations(data["generations"])
        },
        error: function(request, status, error){
            console.log("/req_img error");
            console.log(request)
            console.log(status)
            console.log(error)
        },
        complete: function () { 
            $("#spinner-div").hide()
        },
    }); 
}

function save_img(selected_flowers, form_data, generationURL) {
    let data = {"selected_flowers":selected_flowers,"form_data":form_data, "genURL":generationURL}

    console.log("Saving generated bouquet");
    console.log(data);

    $.ajax({
        type: "POST",
        url: "/save_img",                
        dataType : "json",
        contentType: "application/json; charset=utf-8",
        
        data : JSON.stringify(data),
        success: function(data, text){
            console.log("/save_img success")          
        },
        error: function(request, status, error){
            console.log("/save_img error");
            console.log(request)
            console.log(status)
            console.log(error)
        }
    }); 
}

function show_generations(generations_list){ 
    toggle_visibility(3);
    $("#gallery").empty()

    console.log("Showing generations")
    console.log(generations_list)

    $.each(generations_list, function(i,item){
        let new_gen_div = $("<div class='gen-img'>"+"<img src='"+item+"''></div>")
        
        $("#gallery").append(new_gen_div)
    })
}

// toggles visibility of sections and navigation buttons
// depending on which section is specified to be displayed
// 1 = options
// 2 = flower shop
// 3 = bouquet visualization
function toggle_visibility(num) {
    if (num == 1) {
        console.log("Showing options");

        $("#options_section").show()
        $("#flower_shop_section").hide()
        $("#bouquet_section").hide()

        $("#return_options_btn").hide()
        $("#return_flower_shop_btn").hide()

        $("#submit_btn").show()
        $("#img_btn").hide()
        $("#restart_btn").hide()
    } else if (num == 2) {
        console.log("Showing flowers");

        $("#options_section").hide()
        $("#flower_shop_section").show()
        $("#bouquet_section").hide()

        $("#return_options_btn").show()
        $("#return_flower_shop_btn").hide()

        $("#submit_btn").hide()
        $("#img_btn").show()
        $("#restart_btn").hide()
    } else if (num == 3) {
        console.log("Showing bouquets");

        $("#options_section").hide()
        $("#flower_shop_section").hide()
        $("#bouquet_section").show()

        $("#return_options_btn").hide()
        $("#return_flower_shop_btn").show()

        $("#submit_btn").hide()
        $("#img_btn").hide()
        $("#restart_btn").show()
    }
}