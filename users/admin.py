from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from users.models import User_Customized


# ------------------------------------------------------------------ #
#  Extend the built-in User admin with a link to User_Customized      #
# ------------------------------------------------------------------ #

class UserCustomizedInline(admin.StackedInline):
    model = User_Customized
    can_delete = False
    verbose_name_plural = 'Perfil personalizado'
    fields = ('phone_number', 'avatar', 'puntos')


class UserAdmin(BaseUserAdmin):
    inlines = (UserCustomizedInline,)
    list_display = ('username', 'email', 'first_name', 'last_name')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
