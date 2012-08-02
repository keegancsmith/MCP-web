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
    )
    readonly_fields = ('player1_token', 'player2_token')
    list_filter = ('winner',)
    list_display = ('id', 'player1', 'player2', 'winner',
                    'date_created', 'last_played')
    radio_fields = {'winner': admin.HORIZONTAL}

admin.site.register(TronGame, TronGameAdmin)
