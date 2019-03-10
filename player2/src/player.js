import { app } from "hyperapp";
import ReconnectingWebSocket from "reconnecting-websocket";
import queryString from 'query-string';

import { state, actions, QueueItemStatus } from "./state";
import { view } from "./view";
import {get_protocol, get_hostname, get_ws_port, get_queue_id, is_podium} from "./util";

const player = app(state, actions, view, document.body);
window.player = player; // make this global for debugging


// ====================================================================
// Fetch init data
// ====================================================================

player.check_images();


// ====================================================================
// Network controls
// ====================================================================

function create_websocket() {
    const websocket_url = (
        (get_protocol() === "http:" ? 'ws://' : 'wss://') +
        get_hostname() + get_ws_port() +
        "/ws/"
		// "?queue_id=" + get_queue_id()
    );
    console.log("setup_websocket", websocket_url);

    const socket = new ReconnectingWebSocket(websocket_url);
    socket.onopen = function() {
        console.log("websocket_onopen()");
        player.set_connected(true);
        // player.send("ping"); // auth doesn't actually happen until the first packet
        // now that we're connected, make sure state is in
        // sync for the websocket to send incremental updates
        player.check_settings();
        player.check_queue();
    };
    socket.onclose = function() {
        console.log("websocket_onclose()");
        player.set_connected(false);
    };
    socket.onmessage = function(msg) {
        const cmd = msg.data.trim();
        console.log("websocket_onmessage("+ cmd +")");
        const commands = {
            "queue_updated": player.check_queue,
            "settings": player.check_settings,
        };
        if (cmd in commands) {commands[cmd]();}
        else {console.log("unknown command: " + cmd)}
    };
    return socket;
}
player.set_socket(create_websocket());


// ====================================================================
// Local controls
// ====================================================================

document.onkeydown = function(e) {
    let handled = true;
    switch (e.key) {
        case "s"          : player.set_track_status(QueueItemStatus.SKIPPED); break; // skip
        case "Enter"      : player.set_track_status(QueueItemStatus.PLAYING); break;
        case "Escape"     : player.set_track_status(QueueItemStatus.PENDING); break;
        //case "ArrowLeft"  : player.seek_backwards(); break;
        //case "ArrowRight" : player.seek_forwards(); break;
        case "Space"      : player.set_track_status(QueueItemStatus.PAUSED); break; // TODO: toggle state
        default: handled = false;
    }
    if (handled) {
        e.preventDefault();
    }
};


// ====================================================================
// Auto-play
// ====================================================================

const FPS = 5;
setInterval(
    function() {
        let state = player.get_state();
        if(!state.audio_allowed || state.queue.length === 0) return;

        // if we're waiting for a track to start, and autoplay
        // is enabled, show a countdown
        if(state.queue[0].status !== QueueItemStatus.PLAYING && state.settings["karakara.player.autoplay"] !== 0) {
            if(state.progress >= state.settings["karakara.player.autoplay"]) {player.set_track_status(QueueItemStatus.PLAYING);}
            else {player.set_progress(state.progress + 1/FPS);}
        }
    },
    1000/FPS
);
