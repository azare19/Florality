$(function() {
    $("#saved_bouquets").empty();

    if (ids.length > 0)
        ids.forEach(display_bouquet);
    else
        $("#saved_bouquets").html("Nothing to see here...");
});


function display_bouquet(id) {
    let bouquet = saved[id];

    let url = bouquet.url;
    let colors = bouquet.colors.join(', ');
    let shape = bouquet.shape;
    let vibe = bouquet.vibe;
    let season = bouquet.season;
    let flowers = []

    bouquet.selected_flowers.forEach(function (flower) {
        flowers.push(flower.color + " " + flower.flower)
    })

    let bouquetContainer = $('<div class="bouquet-container"></div>')
    let bouquetInfo = $('<ul class="bouquet-info"></ul>')
    let bouquetImg = $('<img class="bouquet-img" src="' + url + '">')

    let colorsHTML = $('<li>🎨 ' + colors + '</li>')
    let shapeHTML = $('<li>💐 ' + shape + '</li>')
    let vibeHTML = $('<li>💡 ' + vibe + '</li>')
    let seasonHTML = $('<li>📅 ' + season + '</li>')
    let flowersHTML = $('<li>🏵️ ' + flowers.join(', ') + '</li>')

    bouquetInfo.append(flowersHTML);
    bouquetInfo.append(colorsHTML);
    bouquetInfo.append(shapeHTML);
    bouquetInfo.append(vibeHTML);
    bouquetInfo.append(seasonHTML);

    bouquetContainer.append(bouquetImg);
    bouquetContainer.append(bouquetInfo);

    $("#saved_bouquets").append(bouquetContainer);
}