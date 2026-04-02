from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Categoria, Prodotto, Ordine, OrdineProdotto


class AuthTestCase(TestCase):
    """Test autenticazione JWT."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_register(self):
        """Registrazione nuovo utente."""
        res = self.client.post('/api/auth/register/', {
            'username': 'nuovo',
            'email': 'nuovo@test.it',
            'password': 'pass1234'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('username', res.data)

    def test_login(self):
        """Login restituisce access e refresh token."""
        res = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_me_senza_token(self):
        """/auth/me/ senza token deve restituire 401."""
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_con_token(self):
        """/auth/me/ con token restituisce dati utente."""
        login = self.client.post('/api/auth/login/', {
            'username': 'testuser', 'password': 'testpass123'
        }, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + login.data['access'])
        res = self.client.get('/api/auth/me/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'testuser')


class MenuTestCase(TestCase):
    """Test endpoint pubblici del menu."""

    def setUp(self):
        self.client = APIClient()
        self.categoria = Categoria.objects.create(nome='Bevande Calde', descrizione='Calde e buone')
        self.prodotto = Prodotto.objects.create(
            nome='Cappuccino', descrizione='Con latte', prezzo=2.50,
            disponibile=1, categoria=self.categoria
        )

    def test_lista_categorie_pubblica(self):
        """Lista categorie accessibile senza autenticazione."""
        res = self.client.get('/api/categorie/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_lista_prodotti_pubblica(self):
        """Lista prodotti accessibile senza autenticazione."""
        res = self.client.get('/api/prodotti/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filtro_disponibile(self):
        """Filtro ?disponibile=true restituisce solo prodotti disponibili."""
        Prodotto.objects.create(nome='Esaurito', prezzo=1.0, disponibile=0, categoria=self.categoria)
        res = self.client.get('/api/prodotti/?disponibile=true')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for p in res.data['results']:
            self.assertEqual(p['disponibile'], 1)

    def test_filtro_search(self):
        """Filtro ?search= trova prodotti per nome."""
        res = self.client.get('/api/prodotti/?search=Cappuccino')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data['results']) >= 1)


class OrdineTestCase(TestCase):
    """Test endpoint ordini."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='cliente', password='pass1234')
        self.admin = User.objects.create_superuser(username='admin', password='admin1234')
        self.categoria = Categoria.objects.create(nome='Test Cat')
        self.prodotto = Prodotto.objects.create(
            nome='Prodotto Test', prezzo=3.00, disponibile=1, categoria=self.categoria
        )

    def _login(self, username, password):
        res = self.client.post('/api/auth/login/', {'username': username, 'password': password}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + res.data['access'])

    def test_crea_ordine(self):
        """Utente autenticato può creare un ordine."""
        self._login('cliente', 'pass1234')
        res = self.client.post('/api/ordini/', {
            'note': 'Senza zucchero',
            'prodotti': [{'prodotto_id': self.prodotto.id, 'quantita': 2}]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['totale'], 6.00)

    def test_ordine_senza_auth(self):
        """Senza autenticazione non si può creare un ordine."""
        self.client.credentials()
        res = self.client.post('/api/ordini/', {
            'prodotti': [{'prodotto_id': self.prodotto.id, 'quantita': 1}]
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_utente_non_vede_ordini_altrui(self):
        """Un utente normale non può vedere gli ordini di altri."""
        self._login('admin', 'admin1234')
        self.client.post('/api/ordini/', {
            'prodotti': [{'prodotto_id': self.prodotto.id, 'quantita': 1}]
        }, format='json')
        ordine = Ordine.objects.first()

        self._login('cliente', 'pass1234')
        res = self.client.get(f'/api/ordini/{ordine.id}/')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_aggiorna_stato(self):
        """L'admin può aggiornare lo stato di un ordine."""
        self._login('cliente', 'pass1234')
        create_res = self.client.post('/api/ordini/', {
            'prodotti': [{'prodotto_id': self.prodotto.id, 'quantita': 1}]
        }, format='json')
        ordine_id = create_res.data['id']

        self._login('admin', 'admin1234')
        res = self.client.patch(f'/api/ordini/{ordine_id}/stato/', {'stato': 'completato'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['stato'], 'completato')