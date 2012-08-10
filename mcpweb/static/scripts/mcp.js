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
        var cell_size = ui_constants.width / 30;
        var ctx = this.ctx;
        var i;

        ctx.save();

        // Cell contents
        for (i = 0; i < this.game_state.length; i++) {
            var row = this.game_state[i];
            for (var j = 0; j < row.length; j++) {
                ctx.fillStyle = colour_map[row[j]];
                ctx.fillRect(i * cell_size, j * cell_size,
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

function init(urls) {
    var canvas = document.getElementById('canvas');

    // Test for canvas support
    if (canvas.getContext === undefined)
        return;

    tron_game_viewer.init(urls, canvas);
}
