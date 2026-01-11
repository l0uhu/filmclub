from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Film(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='films')
    titre = models.CharField(max_length=200)
    annee = models.CharField(max_length=4, blank=True)
    genre = models.CharField(max_length=200, blank=True)
    synopsis = models.TextField(blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)
    date_visionnage = models.DateField(default='2025-01-01')#date.today)

    def moyenne(self):
        notes = self.notes.all()
        if notes.count() == 0:
            return None
        return round(sum(n.note for n in notes) / notes.count(), 1)

    def __str__(self):
        return self.titre


class Note(models.Model):
    film = models.ForeignKey(Film, related_name='notes', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.IntegerField()

    class Meta:
        unique_together = ('film', 'utilisateur')
