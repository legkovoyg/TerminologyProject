from django.contrib import admin
from .models import RefBook, RefBookElement, RefBookVersion


class RefBookVersionInline(admin.TabularInline):
    model = RefBookVersion
    fields = ('version', 'date')


class RefBookElementInline(admin.TabularInline):
    model = RefBookElement
    fields = ('code', 'value')


@admin.register(RefBook)
class RefBookAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'current_version', 'current_version_date')
    search_fields = ('code', 'name')

    def get_inlines(self, request, obj=None):
        if obj is None:
            return []
        return [RefBookVersionInline]

    def current_version(self, obj):
        from django.utils import timezone
        current_date = timezone.now().date()
        current_version = obj.versions.filter(date__lte=current_date).order_by('-date').first()
        return current_version.version if current_version else "Нет активной версии"

    current_version.short_description = "Текущая версия"

    def current_version_date(self, obj):
        from django.utils import timezone
        current_date = timezone.now().date()
        current_version = obj.versions.filter(date__lte=current_date).order_by('-date').first()
        return current_version.date if current_version else None

    current_version_date.short_description = "Дата начала действия версии"


@admin.register(RefBookVersion)
class RefBookVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'refbook_code', 'refbook_name', 'version', 'date')
    search_fields = ('refbook__code', 'refbook__name', 'version')
    list_filter = ('refbook', 'date')
    inlines = [RefBookElementInline]

    def refbook_code(self, obj):
        return obj.refbook.code

    refbook_code.short_description = "Код справочника"

    def refbook_name(self, obj):
        return obj.refbook.name

    refbook_name.short_description = "Наименование справочника"


@admin.register(RefBookElement)
class RefBookElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'code', 'value')
    search_fields = ('code', 'value')
    list_filter = ('version__refbook', 'version')
