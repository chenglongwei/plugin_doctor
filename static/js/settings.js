function ts_debug_on() {
    var ts_url = document.getElementById('ts_address').value;
    document.getElementById("debugOptionFrame").src = ts_url + "?debug=on";
}

function ts_debug_off() {
    var ts_url = document.getElementById('ts_address').value;
    document.getElementById("debugOptionFrame").src = ts_url + "?debug=off";
}