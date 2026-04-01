from django.contrib import admin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html

from users.models import User_Customized


@admin.register(User_Customized)
class UserCustomizedAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    # ---- column helpers ------------------------------------------------

    @admin.display(description='Email / Usuario', ordering='user__username')
    def col_username(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    @admin.display(description='Nombre completo', ordering='user__first_name')
    def col_full_name(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'.strip() or '—'

    @admin.display(description='Activo', boolean=True, ordering='user__is_active')
    def col_active(self, obj):
        return obj.user.is_active

    @admin.display(description='Puntos', ordering='puntos')
    def col_puntos(self, obj):
        return obj.puntos

    list_display = (
        'col_username',
        'col_full_name',
        'phone_number',
        'col_puntos',
        'col_active',
    )
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')
    ordering = ('user__username',)
    list_per_page = 25

    readonly_fields = ('col_username', 'col_full_name', 'col_active')
    fieldsets = (
        ('Datos del usuario', {
            'fields': ('col_username', 'col_full_name', 'col_active'),
        }),
        ('Perfil', {
            'fields': ('phone_number', 'avatar', 'puntos'),
        }),
    )
