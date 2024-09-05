from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from main.models import Phrase


class CustomUserAdmin(UserAdmin):
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    # list_display = [
    #     "email",
    #     "username",
    # ]
    list_display = ["username", "is_staff", "native_language", "working_on"]
    fieldsets = (
        ("User Settings", {"fields": ("native_language", "working_on")}),
        ("Username/Password", {"fields": ("username", "password")}),
        # ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permissions",
            {
                "fields": (
                    # "is_active",
                    "is_staff",
                    "is_superuser",
                    # "groups",
                    # "user_permissions",
                )
            },
        ),
        # ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_staff = True
            # grant all permission
            # note that this isn't too secure
            # content_type = ContentType.objects.get_for_model(obj)

            # user = obj
            # permissions_for_phrase_model = Permission.objects.filter(
            #     content_type=ContentType.objects.get_for_model(Phrase)
            # )
            # obj.user_permissions.add(*permissions_for_phrase_model)
            # user.save()
        # obj.save()
        super().save_model(request, obj, form, change)
        permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(Phrase)
        )
        obj.user_permissions.add(*permissions)

        permissions = Permission.objects.filter(
            content_type=ContentType.objects.get_for_model(CustomUser)
        )
        obj.user_permissions.add(*permissions)

        # all_phrase_permissions = ContentType.objects.get_for_model(Phrase)

        # user = obj
        # permissions_for_phrase_model = Permission.objects.filter(
        #     content_type=ContentType.objects.get_for_model(Phrase)
        # )

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return [
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ]
        else:
            return [
                "is_active",
                "is_staff",
                # "is_superuser",
                "groups",
                "user_permissions",
            ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Return all objects for superusers
        return qs.filter(id=request.user.id)  # Filter objects for regular users


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.unregister(Group)
