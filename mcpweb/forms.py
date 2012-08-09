from mcpweb.models import TronGame

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class NewTronGameForm(forms.Form):
    player2 = forms.ModelChoiceField(queryset=User.objects.all(),
                                     label='Player 2', required=True)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Create Game'))
        self.helper.form_action = reverse('new-tron-game')

        super(NewTronGameForm, self).__init__(*args, **kwargs)

    def create_game(self, user):
        tg = TronGame(player1=user, player2=self.cleaned_data['player2'])
        tg.save()
        return tg
