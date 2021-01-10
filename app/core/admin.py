from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# _ => translate string into humman readable text = translate
from django.utils.translation import gettext as _

from core import models


# Extends the BasedUserAdmin
class UserAdmin(BaseUserAdmin):
    # Ordering by id
    ordering = ['id']
    # List them by email and name
    list_display = ['email', 'name']
    # define the sections for the fieldsets for the change and create page
    # To add more fields, simple exteand the fields
    fieldsets = (
        # None=the title for the section
        (None, {'fields': ('email', 'password')}),
        # The personal info section
        # When providing one field, make sure to include ','
        (_('Personal Info'), {'fields': ('name',)}),
        # The permission section - the permission that control the user
        (
            _('Permissions'),
            {
                'fields': ('is_active', 'is_staff', 'is_superuser')
            }
        ),
        # Importand dates section
        (_('Important dates'), {'fields': ('last_login',)})
    )
    # customise the add_fieldsets (add page)
    add_fieldsets = (
        # None=the title for the section
        (None, {
            # The fields that we include
            # The default classes that assigned to the form
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


# Register our useradamin to the admin
admin.site.register(models.User, UserAdmin)
# Register the Tag model to the admin (no need for a speacil Useradmin)
admin.site.register(models.Tag)
# Register the Ingredient model to the admin (no need for a speacil Useradmin)
admin.site.register(models.Ingredient)
