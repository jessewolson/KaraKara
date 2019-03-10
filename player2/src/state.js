import {get_lyrics, api} from "./util";


// ====================================================================
// State constants
// ====================================================================

const QueueItemStatus = {
    PENDING: "pending",
    PAUSED: "paused",
    PLAYING: "playing",
    PLAYED: "played",
    SKIPPED: "skipped",
    REMOVED: "removed",
};


// ====================================================================
// State and state management functions
// ====================================================================

const state = {
    // global app bits
    connected: false,
    audio_allowed: (new AudioContext()).state === "running",
    socket: null,

    // managed by check_settings / set_settings
    settings: {
        "karakara.player.title"               : "KaraKara",
        "karakara.player.theme"               : "metalghosts",
        "karakara.player.video.preview_volume":  0.2,
        "karakara.player.video.skip.seconds"  : 20,
        "karakara.player.autoplay"            : 0, // Autoplay after X seconds
        "karakara.player.subs_on_screen"      : true, // Set false if using podium
        "karakara.event.end"                  : null,
        "karakara.podium.video_lag"           : 0.50,  // adjust to get podium and projector in sync
        "karakara.podium.soft_sub_lag"        : 0.35,  // adjust to get soft-subs and hard-subs in sync
    },

    // managed by check_images / set_images
    images: [],

    // managed by check_queue / set_queue
    queue: [],

    // managed by set_progress (called from video.onTimeUpdate)
    progress: 0,
};

const actions = {
    // this has nothing to do with the player, we just need
    // to make sure that the user has clicked in order for
    // chrome to allow auto-play.
    click: () => () => ({ audio_allowed: true }),

    // general application state
    get_state: () => state => state,
    set_socket: value => () => ({ socket: value }),
    set_connected: value => () => ({ connected: value }),
    set_progress: value => () => ({ progress: value }),

    // handle settings updates
    check_settings: () => (state, actions) => {
        api(state, "GET", "settings", {}, function(data) {
            actions.set_settings(Object.assign(state.settings, data.settings));
        });
    },
    set_settings: value => () => ({ settings: value }),

    // handle playlist updates
    check_queue: () => (state, actions) => {
        api(state, "GET", "queue_items", {}, function(data) {
            function merge_lyrics(item) {
                item.track.lyrics = get_lyrics(state, item.track);
                return item;
            }
            let queue_with_lyrics = data.queue.map((item) => merge_lyrics(item));
            actions.set_queue(queue_with_lyrics);
        });
    },
    set_queue: value => (state, actions) => ({ queue: value }),

    // thumbnail rain data fetching
    check_images: () => (state, actions) => {
        api(state, "GET", "random_images", {count: 25}, function(data) {
            let n=0;
            actions.set_images(data.images.map(function(fn) {
                return {
                    filename: fn,
                    x: (n++ / data.images.length),
                    delay: Math.random() * 10,
                }
            }));
        });
    },
    set_images: value => () => ({ images: value }),

    // Tell the network what to do
    set_track_status: value => (state, actions) => {
        api(state, "PUT", "queue_items", {
            "queue_item.id": state.queue[0].id,
            "status": value,
            "uncache": new Date().getTime()
        }, function(data) {
            // Server should broadcast a queue-update message, let's
            // wait and get that at the same time as everyone else
            // actions.check_queue();
        });
    },
};

export {state, actions, QueueItemStatus};
