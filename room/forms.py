from django import forms

class SearchForm(forms.Form):
    league = forms.IntegerField(required=True, label='', attrs={'class': 'indexinput'})
