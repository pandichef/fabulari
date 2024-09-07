from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .models import CustomUser
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from main.models import Phrase


class CustomUserAdmin(UserAdmin):
    # change_form_template = "change_form_with_export_button.html"
    change_form_template = "change_form_without_history_button.html"
    # add_form = CustomUserCreationForm
    # form = CustomUserChangeForm
    model = CustomUser
    # list_display = [
    #     "email",
    #     "username",
    # ]
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        # extra_context["save_on_top"] = True
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        # extra_context["show_close"] = False
        # extra_context["show_history"] = False
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def add_view(self, request, form_url="", extra_context=None):
        # def add_view(self, request, object_id, form_url="", extra_context=None):
        # obj = self.get_object(request, object_id)
        extra_context = extra_context or {}
        # extra_context["save_on_top"] = True
        extra_context["show_save"] = False
        extra_context["show_save_and_add_another"] = False
        # extra_context["show_history"] = False
        # return super().change_view(
        #     request, object_id, form_url, extra_context=extra_context
        # )
        return self.changeform_view(request, None, form_url, extra_context)

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
                    "user_permissions",
                )
            },
        ),
        # ("Important dates", {"fields": ("last_login", "date_joined")}),
        (
            "Readwise Integration",
            {"fields": ("readwise_api_key", "last_readwise_update")},
        ),
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

        content_type = ContentType.objects.get_for_model(CustomUser)
        # permissions = Permission.objects.filter(
        #     content_type=ContentType.objects.get_for_model(CustomUser)
        # )

        view_permission = Permission.objects.get(
            content_type=content_type, codename="view_customuser"
        )
        change_permission = Permission.objects.get(
            content_type=content_type, codename="change_customuser"
        )
        obj.user_permissions.add(view_permission, change_permission)

        # all_phrase_permissions = ContentType.objects.get_for_model(Phrase)

        # user = obj
        # permissions_for_phrase_model = Permission.objects.filter(
        #     content_type=ContentType.objects.get_for_model(Phrase)
        # )

    def get_readonly_fields(self, request, obj=None):
        fields = [
            "is_active",
            # "is_staff",
            # "is_superuser",
            # "last_readwise_update",
        ]
        # if request.user.readwise_api_key:
        #     fields += [
        #         "last_readwise_update",
        #     ]
        if request.user.is_superuser:
            return fields
        else:
            # extra fields for non-superuser
            return fields + [
                "is_staff",
                "is_superuser",
                "user_permissions",
                "groups",
            ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Return all objects for superusers
        return qs.filter(id=request.user.id)  # Filter objects for regular users

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove all actions
        actions.clear()
        return actions


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.unregister(Group)
