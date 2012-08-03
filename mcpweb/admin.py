from django.contrib import admin
from mcpweb.models import TronGame


class TronGameAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': (('player1', 'player2'),
                       'winner', 'description',
                       ('player1_token', 'player2_token'))
        }),
        ('Advanced', {
            'classes': ('collapse',),
            'fields': ('turn',
                       ('date_created', 'last_played'),
                       'game_state')
        }),
        ('Readonly Properties', {
            'classes': ('collapse',),
            'fields': (('players', 'winners'),
                       ('current_player', 'current_user')),
        }),
    )
    readonly_fields = ('player1_token', 'player2_token',
                       'current_player', 'current_user', 'winners', 'players')
    list_filter = ('winner',)
    list_display = ('id', 'player1', 'player2', 'winner',
                    'date_created', 'last_played')
    radio_fields = {'winner': admin.HORIZONTAL}

admin.site.register(TronGame, TronGameAdmin)
