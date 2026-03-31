from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    nome = models.TextField()
    descrizione = models.TextField(null=True, blank=True)

    class Meta:
        managed = False          # tabella già esistente nel db fornito
        db_table = 'categoria'

    def __str__(self):
        return self.nome


class Prodotto(models.Model):
    nome = models.TextField()
    descrizione = models.TextField(null=True, blank=True)
    prezzo = models.FloatField()
    disponibile = models.IntegerField(default=1)   #1= disponibile, 0=esaurito
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='categoria_id',
        related_name='prodotti',
    )
    immagine_url = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'prodotto'

    def __str__(self):
        return self.nome


class Ordine(models.Model):
    STATI = [
        ('in_attesa', 'In Attesa'),
        ('in_preparazione', 'In Preparazione'),
        ('completato', 'Completato'),
        ('annullato', 'Annullato'),
    ]

    utente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='utente_id',
        related_name='ordini',
    )
    data_ordine = models.DateTimeField(auto_now_add=True)
    stato = models.TextField(default='in_attesa')
    totale = models.FloatField(default=0.0)
    note = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'ordine'

    def __str__(self):
        return f'Ordine #{self.id} - {self.utente.username}'


class OrdineProdotto(models.Model):
    ordine = models.ForeignKey(
        Ordine,
        on_delete=models.CASCADE,
        db_column='ordine_id',
        related_name='prodotti_ordine',
    )
    prodotto = models.ForeignKey(
        Prodotto,
        on_delete=models.CASCADE,
        db_column='prodotto_id',
    )
    quantita = models.IntegerField(default=1)

    class Meta:
        managed = False
        db_table = 'ordine_prodotto'

    def __str__(self):
        return f'{self.quantita}x {self.prodotto.nome} (ordine #{self.ordine_id})'
