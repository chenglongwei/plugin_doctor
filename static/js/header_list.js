function filter_hook_plugin() {
    var request_url = "/";

    var hook_ids = $('#hook_id').val();
    if (hook_ids != null && hook_ids.indexOf("ALL_HOOKs") > -1) {
        hook_ids = "ALL_HOOKs";
    }

    if (hook_ids != null) {
        request_url += "?hooks=" + hook_ids;
    }

    var plugin_name = $('#plugin_name').val();
    if (plugin_name != null && plugin_name.indexOf("ALL_Plugins") > -1) {
        plugin_name = "ALL_Plugins";
    }

    if (plugin_name != null) {
        request_url += "&plugins=" + plugin_name;
    }

    window.location.href = request_url
}