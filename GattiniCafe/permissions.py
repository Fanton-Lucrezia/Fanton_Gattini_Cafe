from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Permesso personalizzato:
    - lettura (GET, HEAD, OPTIONS) → aperta a tutti
    - scrittura (POST, PUT, PATCH, DELETE) → solo utenti is_staff
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrAdmin(BasePermission):
    """
    Permesso a livello di oggetto:
    - l'utente può vedere/modificare solo i propri ordini
    - gli admin vedono tutto
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.utente == request.user
