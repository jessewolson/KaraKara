<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>

<script>
    function set_track_status(message) {
        alert("TODO: call the set-track-status API");
        return false;
    }
</script>

<%
    skip_sec = request.queue.settings['karakara.player.video.skip.seconds']
    buttons = (
        ('playing'       , _('mobile.remote.play')),
        ('paused'        , _('mobile.remote.pause')),
        #('seek_forwards' , _('mobile.remote.seek +${skip_sec}', mapping={'skip_sec': skip_sec})),
        #('seek_backwards', _('mobile.remote.seek -${skip_sec}', mapping={'skip_sec': skip_sec})),
        ('pending'       , _('mobile.remote.stop')),
        ('skipped'       , _('mobile.remote.skip')),
    )
%>
% for cmd, title in buttons:
    <a href='?cmd=${cmd}' data-role="button" onclick='return set_track_status("${cmd}");'>${title}</a>
% endfor
