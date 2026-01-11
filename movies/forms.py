from django import forms
from .models import Film, Note
from datetime import date

class TMDBSearchForm(forms.Form):
    query = forms.CharField(
        label="Rechercher un film (TMDB)", 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du film'})
    )

class FilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['titre', 'annee', 'genre', 'date_visionnage']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'annee': forms.NumberInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'date_visionnage': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mettre par défaut l'année courante
        if not self.instance.pk:
            today = date.today()
            self.initial['date_visionnage'] = '2025-01-01'#today

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['note']
        widgets = {
            'note': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5, 'step': 0.5})
        }
