from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Categoria, Prodotto, Ordine, OrdineProdotto


# Auth ------------------------------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    """Serializer per la registrazione di un nuovo utente."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer per i dati dell'utente autenticato (/api/auth/me/)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'date_joined']


# ─── Menu ────────────────────────────────────────────────────────────────────

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descrizione']


class ProdottoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Prodotto
        fields = ['id', 'nome', 'descrizione', 'prezzo', 'disponibile',
                  'categoria', 'categoria_nome', 'immagine_url']


# Ordini -----------------------------------------------------------------

class OrdineProdottoInputSerializer(serializers.Serializer):
    """Usato in input durante la creazione di un ordine."""
    prodotto_id = serializers.IntegerField()
    quantita = serializers.IntegerField(min_value=1)

    def validate_prodotto_id(self, value):
        try:
            prodotto = Prodotto.objects.get(pk=value)
        except Prodotto.DoesNotExist:
            raise serializers.ValidationError(f'Prodotto con id {value} non trovato.')
        if not prodotto.disponibile:
            raise serializers.ValidationError(f'Il prodotto "{prodotto.nome}" non è disponibile.')
        return value


class OrdineProdottoReadSerializer(serializers.ModelSerializer):
    """Usato in output per mostrare i prodotti di un ordine."""
    prodotto_id = serializers.IntegerField()
    prodotto_nome = serializers.CharField(source='prodotto.nome', read_only=True)
    prodotto_prezzo = serializers.FloatField(source='prodotto.prezzo', read_only=True)

    class Meta:
        model = OrdineProdotto
        fields = ['prodotto_id', 'prodotto_nome', 'prodotto_prezzo', 'quantita']


class OrdineReadSerializer(serializers.ModelSerializer):
    """Serializer di lettura per gli ordini."""
    prodotti = OrdineProdottoReadSerializer(source='prodotti_ordine', many=True, read_only=True)
    utente_username = serializers.CharField(source='utente.username', read_only=True)

    class Meta:
        model = Ordine
        fields = ['id', 'utente_id', 'utente_username', 'data_ordine',
                  'stato', 'totale', 'note', 'prodotti']


class OrdineCreateSerializer(serializers.Serializer):
    """Serializer di scrittura per creare un nuovo ordine."""
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    prodotti = OrdineProdottoInputSerializer(many=True)

    def validate_prodotti(self, value):
        if not value:
            raise serializers.ValidationError('L\'ordine deve contenere almeno un prodotto.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        prodotti_data = validated_data.get('prodotti', [])

        #Calcola il tot
        totale = 0.0
        for item in prodotti_data:
            prodotto = Prodotto.objects.get(pk=item['prodotto_id'])
            totale += prodotto.prezzo * item['quantita']

        # Crea l'ordine
        ordine = Ordine.objects.create(
            utente=user,
            note=validated_data.get('note', ''),
            totale=round(totale, 2),
            stato='in_attesa',
        )

        #Crea le righe ordine-prodotto
        for item in prodotti_data:
            OrdineProdotto.objects.create(
                ordine=ordine,
                prodotto_id=item['prodotto_id'],
                quantita=item['quantita'],
            )

        return ordine


class StatoUpdateSerializer(serializers.Serializer):
    """Serializer per aggiornare solo lo stato di un ordine (admin only)."""
    STATI_VALIDI = ['in_attesa', 'in_preparazione', 'completato', 'annullato']
    stato = serializers.ChoiceField(choices=STATI_VALIDI)
