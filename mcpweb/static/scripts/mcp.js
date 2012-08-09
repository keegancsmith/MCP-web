var tron_game_viewer = {
    urls: null,
    canvas: null,
    ctx: null,
    state: null,
    game_state: null,
    cell_size: 450 / 30,

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
        var old_state = this.state;
        this.state = state;
        setTimeout($.proxy(this, 'fetch'), 2000);
        // Only redraw if something changed
        if (old_state === null || old_state.turn != state.turn) {
            this.parse_game_state();
            this.draw();
        }
    },

    parse_game_state: function() {
        this.game_state = [];
        var i = 0;
        for (i = 0; i < 30 * 30; i++) {
            if (i % 30 == 0)
                this.game_state.push([]);
            this.game_state[this.game_state.length - 1].push('');
        }

        var lines = this.state.game_state.split('\r\n');
        for (i = 0; i < lines.length; i++) {
            var tokens = lines[i].split(' ');
            if (tokens.length == 3) {
                var x = parseInt(tokens[0]);
                var y = parseInt(tokens[1]);
                this.game_state[x][y] = tokens[2];
            }
        }
    },

    draw: function() {
        var colour_map = {
            You: '#e5001e',
            YourWall: '#ff5d51',
            Opponent: '#004de5',
            OpponentWall: '#38c6e2',
            Clear: '#7cff82'
        };

        for (var i = 0; i < this.game_state.length; i++) {
            var row = this.game_state[i];
            for (var j = 0; j < row.length; j++) {
                this.ctx.fillStyle = colour_map[row[j]];
                this.ctx.fillRect(i * this.cell_size, j * this.cell_size,
                                  this.cell_size, this.cell_size);
            }
        }
    }
};

function init(urls) {
    var canvas = document.getElementById('canvas');

    // Test for canvas support
    if (canvas.getContext === undefined)
        return;

    tron_game_viewer.init(urls, canvas);
}
