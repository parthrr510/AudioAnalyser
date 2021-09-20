from django import forms

class AudioForm(forms.Form):
    """ To Input the Audio as a form"""
    audio = forms.FileField(label='Audio')