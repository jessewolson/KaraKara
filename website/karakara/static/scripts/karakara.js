$.cookie.json = true;

var priority_token_cookie = $.cookie('priority_token');
var server_datetime_offset;
var interval_id;

function update_priority_token_feedback() {
    if (priority_token_cookie) {
        var valid_start = new Date(priority_token_cookie.valid_start);
        var valid_end   = new Date(priority_token_cookie.valid_end  );
        if (!server_datetime_offset) {
            server_datetime_offset = new Date() - new Date(priority_token_cookie.server_datetime);
        }
        var now = new Date() - server_datetime_offset;
        var delta_start = valid_start - now;
        var delta_end   = valid_end   - now;
        
        if (delta_end < 0) {
            $.removeCookie('priority_token');
            clearInterval(interval_id);
            priority_token_cookie = null;
            server_datetime_offset = null;
            $("#priority_countdown")[0].innerHTML = "";
            console.log("Deleted stale 'priority_token' cookie");
        }
        if (delta_start > 0) {
            console.log("Priority Mode in "+timedelta_str(delta_start));
            $("#priority_countdown")[0].innerHTML = "pmode in "+timedelta_str(delta_start);
        }
        if (delta_start < 0 && delta_end > 0) {
            $("#priority_countdown")[0].innerHTML = "pmode for "+timedelta_str(delta_end);
        }
    }
}

$(document).ready(function() {
    if (priority_token_cookie) {
        interval_id = setInterval(update_priority_token_feedback, 1000);
        update_priority_token_feedback();
    }
});
