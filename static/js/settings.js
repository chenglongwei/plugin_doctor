function ts_debug_on() {
    var ts_url = document.getElementById('ts_address').value;
    document.getElementById("debugOptionFrame").src = ts_url + "?debug=on";
}

function ts_debug_off() {
    var ts_url = document.getElementById('ts_address').value;
    document.getElementById("debugOptionFrame").src = ts_url + "?debug=off";
}

function ts_http_request() {
    var request_url = document.getElementById('ts_request_url').value;

    var hook_ids = $('#hook_id').val();
    if (hook_ids != null && hook_ids.indexOf("ALL_HOOKs") > -1) {
        hook_ids = "ALL_HOOKs";
    }

    if (hook_ids != null) {
        request_url += "?hooks=" + hook_ids;
    }

    document.getElementById("debugOptionFrame").src = request_url;
}