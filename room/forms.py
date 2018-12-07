from django import forms

class SearchForm(forms.Form):
    league = forms.IntegerField(required=True, label='', widget=forms.TextInput(attrs={'class': "indexinput",},)
