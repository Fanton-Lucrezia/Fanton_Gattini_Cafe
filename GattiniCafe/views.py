from django.shortcuts import render

# Create your views here.
from django.contrib.auth.models import User
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Categoria, Prodotto, Ordine, OrdineProdotto
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    CategoriaSerializer,
    ProdottoSerializer,
    OrdineReadSerializer,
    OrdineCreateSerializer,
    StatoUpdateSerializer,
)

from django.utils.timezone import now
from django.db.models import Sum, Count, F


# Auth -------------------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Registra un nuovo utente.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    """
    GET /api/auth/me/
    Restituisce i dati dell'utente attualmente autenticato.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


# Categorie -------------------------------------------------------------------

class CategoriaViewSet(viewsets.ModelViewSet):
    """
    GET    /api/categorie/       → lista categorie (pubblico)
    GET    /api/categorie/{id}/  → dettaglio categoria (pubblico)
    POST   /api/categorie/       → crea categoria (solo admin)
    PUT    /api/categorie/{id}/  → modifica categoria (solo admin)
    DELETE /api/categorie/{id}/  → elimina categoria (solo admin)
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]


# Prodotti -------------------------------------------------------------------


class ProdottoViewSet(viewsets.ModelViewSet):
    """
    GET    /api/prodotti/       → lista prodotti (pubblico, con filtri)
    GET    /api/prodotti/{id}/  → dettaglio prodotto (pubblico)
    POST   /api/prodotti/       → crea prodotto (solo admin)
    PUT    /api/prodotti/{id}/  → modifica prodotto (solo admin)
    PATCH  /api/prodotti/{id}/  → aggiornamento parziale (solo admin)
    DELETE /api/prodotti/{id}/  → elimina prodotto (solo admin)

    Query parameter supportati:
      ?categoria=<id>        → filtra per categoria
      ?disponibile=true      → solo prodotti disponibili
      ?search=<testo>        → ricerca per nome o descrizione
    """
    serializer_class = ProdottoSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Prodotto.objects.select_related('categoria').all()

        # Filtro per categoria
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)

        #Filtro per disponibilità
        disponibile = self.request.query_params.get('disponibile')
        if disponibile and disponibile.lower() == 'true':
            qs = qs.filter(disponibile=1)

        #Ricerca per nome o descrizione
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(nome__icontains=search) | qs.filter(descrizione__icontains=search)

        return qs


# Ordini -------------------------------------------------------------------

class OrdineViewSet(viewsets.ViewSet):
    """
    GET    /api/ordini/             → lista ordini (propri, o tutti se admin)
    POST   /api/ordini/             → crea nuovo ordine
    GET    /api/ordini/{id}/        → dettaglio ordine
    PATCH  /api/ordini/{id}/stato/  → aggiorna stato (solo admin)
    """
    permission_classes = [IsAuthenticated]

    def _get_ordine_or_403(self, request, pk):
        """Helper: recupera l'ordine e verifica i permessi."""
        try:
            ordine = Ordine.objects.prefetch_related('prodotti_ordine__prodotto').get(pk=pk)
        except Ordine.DoesNotExist:
            return None, Response({'detail': 'Ordine non trovato.'}, status=status.HTTP_404_NOT_FOUND)

        #Permesso: admin vede tutto, utente normale solo i suoi
        if not request.user.is_staff and ordine.utente != request.user:
            return None, Response({'detail': 'Non hai il permesso di accedere a questo ordine.'},
                                  status=status.HTTP_403_FORBIDDEN)
        return ordine, None

    def list(self, request):
        """GET /api/ordini/"""
        if request.user.is_staff:
            ordini = Ordine.objects.prefetch_related('prodotti_ordine__prodotto').all().order_by('-data_ordine')
        else:
            ordini = Ordine.objects.prefetch_related('prodotti_ordine__prodotto').filter(
                utente=request.user
            ).order_by('-data_ordine')

        data_da = request.query_params.get('data_da')  # es. 2024-11-01
        data_a = request.query_params.get('data_a')  # es. 2024-11-30
        if data_da:
            ordini = ordini.filter(data_ordine__date__gte=data_da)
        if data_a:
            ordini = ordini.filter(data_ordine__date__lte=data_a)

        serializer = OrdineReadSerializer(ordini, many=True)
        return Response(serializer.data)

    def create(self, request):
        """POST /api/ordini/"""
        serializer = OrdineCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ordine = serializer.save()
            #Rilegge l'ordine con i prodotti per la risposta
            ordine.refresh_from_db()
            read_serializer = OrdineReadSerializer(
                Ordine.objects.prefetch_related('prodotti_ordine__prodotto').get(pk=ordine.pk)
            )
            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """GET /api/ordini/{id}/"""
        ordine, error = self._get_ordine_or_403(request, pk)
        if error:
            return error
        serializer = OrdineReadSerializer(ordine)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='stato')
    def aggiorna_stato(self, request, pk=None):
        """PATCH /api/ordini/{id}/stato/ — solo admin"""
        if not request.user.is_staff:
            return Response({'detail': 'Solo gli admin possono aggiornare lo stato.'},
                            status=status.HTTP_403_FORBIDDEN)

        ordine, error = self._get_ordine_or_403(request, pk)
        if error:
            return error

        serializer = StatoUpdateSerializer(data=request.data)
        if serializer.is_valid():
            ordine.stato = serializer.validated_data['stato']
            ordine.save()
            read_serializer = OrdineReadSerializer(
                Ordine.objects.prefetch_related('prodotti_ordine__prodotto').get(pk=ordine.pk)
            )
            return Response(read_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Statistiche admin -------------------------------------------------------------------

class AdminStatsView(APIView):
    """
    GET /api/admin/stats/  —  solo admin
    Restituisce:
      - numero ordini per stato
      - prodotto più venduto
      - incasso totale del giorno
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Ordini per stato
        ordini_per_stato = (
            Ordine.objects
            .values('stato')
            .annotate(totale_ordini=Count('id'))
        )

        # Prodotto più venduto (per quantità totale ordinata)
        prodotto_piu_venduto = (
            OrdineProdotto.objects
            .values('prodotto__id', 'prodotto__nome')
            .annotate(quantita_totale=Sum('quantita'))
            .order_by('-quantita_totale')
            .first()
        )

        # Incasso totale del giorno
        oggi = now().date()
        incasso_oggi = (
            Ordine.objects
            .filter(data_ordine__date=oggi, stato__in=['in_attesa', 'in_preparazione', 'completato'])
            .aggregate(incasso=Sum('totale'))
        )

        return Response({
            'ordini_per_stato': list(ordini_per_stato),
            'prodotto_piu_venduto': prodotto_piu_venduto,
            'incasso_oggi': incasso_oggi['incasso'] or 0.0,
        })