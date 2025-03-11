document.addEventListener("DOMContentLoaded", function() {
    console.log("marker_click.js loaded");
    var greenIcon = L.icon({
        iconUrl: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });
    if (typeof myMap !== "undefined" && myMap) {
        console.log("myMap is defined:", myMap);
        myMap.eachLayer(function(layer) {
            if (layer instanceof L.Marker) {
                console.log("Attaching click event to marker:", layer);
                layer.on('click', function(e) {
                    this.setIcon(greenIcon);
                });
            }
        });
    } else {
        console.error("myMap is not defined.");
    }
});
