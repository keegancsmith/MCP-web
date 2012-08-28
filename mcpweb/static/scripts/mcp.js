var ui_constants = {
    width: 500,
    height: 600
};

var tron_game_viewer = {
    urls: null,
    canvas: null,
    ctx: null,
    state: null,
    game_state: null,
    pause: false,

    init: function(urls, canvas) {
        this.urls = urls;
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        setTimeout($.proxy(this, 'fetch'), 0);
    },

    fetch: function() {
        // Only fetch state if we don't have it or the game is ongoing
        if (this.state === null || this.state.winners.length == 0) {
            $.get(this.urls.game, {}, $.proxy(this, 'post_fetch'));
        }
    },

    post_fetch: function(state) {
        if (this.pause)
            return;
        var old_state = this.state;
        this.state = state;
        setTimeout($.proxy(this, 'fetch'), 2000);
        // Only redraw if something changed
        if (old_state === null || old_state.turn != state.turn) {
            this.game_state = this.parse_game_state();
            this.draw();
        }
    },

    _empty_game_state: function() {
        var game_state = [];
        for (var i = 0; i < 30 * 30; i++) {
            if (i % 30 == 0)
                game_state.push([]);
            game_state[game_state.length - 1].push('');
        }
        return game_state;
    },

    parse_game_state: function() {
        var game_state = this._empty_game_state();
        var lines = this.state.game_state.split('\r\n');
        for (var i = 0; i < lines.length; i++) {
            var tokens = lines[i].split(' ');
            if (tokens.length == 3) {
                var x = parseInt(tokens[0]);
                var y = parseInt(tokens[1]);
                game_state[y][x] = tokens[2];
            }
        }
        return game_state;
    },

    draw: function() {
        var colour_map = {
            You: '#e5001e',
            YourWall: '#ff5d51',
            Opponent: '#004de5',
            OpponentWall: '#38c6e2',
            Clear: '#7cff82'
        };
        var cell_size = ui_constants.width / 30;
        var ctx = this.ctx;
        var i;

        ctx.save();

        // Cell contents
        for (i = 0; i < this.game_state.length; i++) {
            var row = this.game_state[i];
            for (var j = 0; j < row.length; j++) {
                ctx.fillStyle = colour_map[row[j]];
                ctx.fillRect(j * cell_size, i * cell_size,
                             cell_size, cell_size);
            }
        }

        // Legend
        function legend(y, colour, text) {
            var x = cell_size * 3;
            ctx.fillStyle = colour;
            ctx.fillRect(x, y, cell_size, cell_size);
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = 'black';
            ctx.font = 'bold 16px sans-serif';
            ctx.fillText(text, x + cell_size * 1.3, y + cell_size / 2);
        }
        legend(cell_size * 30.5, colour_map['You'],
               'Player 1 - ' + this.state.players[0].username);
        legend(cell_size * 32.5, colour_map['Opponent'],
               'Player 2 - ' + this.state.players[1].username);

        // Grid
        function draw_line(x1, y1, x2, y2) {
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();
        }
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.lineWidth = 1;
        for (i = 0; i <= 30; i++) {
            var offset = i * cell_size;
            draw_line(offset, 0, offset, ui_constants.width);
            draw_line(0, offset, ui_constants.width, offset);
        }

        ctx.restore();
    }
};


var tron_history = {
    history: null,
    p1_moves: 0,
    p2_moves: 0,
    tick: 0,
    tick_speed: 250,
    tick_timer: null,

    animate_history: function(tick_speed) {
        this.tick_speed = tick_speed;
        $.get(tron_game_viewer.urls.history, {}, $.proxy(this, 'post_fetch'));
    },

    post_fetch: function(resp) {
        if (this.tick_timer !== null) {
            clearTimeout(this.tick_timer);
            this.tick_timer = null;
        }

        tron_game_viewer.pause = true;
        this.history = resp.history;
        this.p1_moves = resp.p1_moves;
        this.p2_moves = resp.p2_moves;
        this.tick = 0;
        this.tick_timer = setTimeout($.proxy(this, 'history_tick'), 0);
    },

    history_tick: function() {
        tron_game_viewer.game_state = this.parse_game_history();
        tron_game_viewer.draw();

        var max_ticks = this.p1_moves + this.p2_moves - 2;
        var progress = $('#replay-progress');

        this.tick++;
        if (this.tick <= max_ticks) {
            this.tick_timer = setTimeout($.proxy(this, 'history_tick'), this.tick_speed);
            progress.addClass('active');
            progress.find('.bar').attr('style', 'width: ' + (this.tick / max_ticks) * 100 + '%;');
        } else {
            this.tick_timer = null;
            progress.removeClass('active');
            tron_game_viewer.pause = false;
            tron_game_viewer.state = null;
            tron_game_viewer.fetch();
        }
    },

    parse_game_history: function() {
        var game_state = tron_game_viewer._empty_game_state();
        var max_p1 = Math.floor((this.tick - 1) / 2 + 2);
        var min_p2 = -Math.floor(this.tick / 2 + 1);
        if (this.tick == 0) {
            max_p1 = 1;
            min_p2 = -1;
        }

        for (var i = 0; i < 30; i++) {
            var row = game_state[i];
            var hist_row = this.history[i];
            for (var j = 0; j < 30; j++) {
                var turn = hist_row[j];
                if (turn == 0 || turn < min_p2 || turn > max_p1) {
                    row[j] = 'Clear';
                } else if (turn > 0) {
                    row[j] = turn == max_p1 ? 'You' : 'YourWall';
                } else {
                    row[j] = turn == min_p2 ? 'Opponent' : 'OpponentWall';
                }
            }
        }

        return game_state;
    }
};

function init(urls) {
    var canvas = document.getElementById('canvas');

    // Test for canvas support
    if (canvas.getContext === undefined)
        return;

    tron_game_viewer.init(urls, canvas);
}
