document.addEventListener("DOMContentLoaded", function () {
    console.log("marker_click.js loaded");

    let checkMapInterval = setInterval(() => {
        if (typeof myMap !== "undefined" && myMap) {
            clearInterval(checkMapInterval);
            console.log("myMap detected:", myMap);

            myMap.eachLayer(function (layer) {
                if (layer instanceof L.Marker) {
                    console.log("Attaching click event to marker:", layer);

                    layer.on("click", function () {
                        // Check if marker already has an icon
                        let currentIcon = layer.options.icon;

                        if (!currentIcon) {
                            console.error("Marker icon is undefined:", layer);
                            return;
                        }

                        // Toggle color between red and green
                        let newColor = currentIcon.options.markerColor === "red" ? "green" : "red";

                        // Create new Leaflet AwesomeMarker icon
                        let newIcon = L.AwesomeMarkers.icon({
                            icon: "info-sign",
                            markerColor: newColor,
                            prefix: "glyphicon"
                        });

                        layer.setIcon(newIcon);
                        console.log("Marker clicked, color changed to:", newColor);
                    });
                }
            });
        }
    }, 100);
});
