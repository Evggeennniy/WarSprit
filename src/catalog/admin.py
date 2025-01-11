from django.contrib import admin
from django.forms import TextInput
from django.utils.safestring import mark_safe

from .models import Category, ProductImage, ProductOption, Product, OrderProductPart, Order, Color, \
    ProductOptionGroup, OrderOptionsProductPart


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("name",)

    search_fields = ("id", "name")

    readonly_fields = ()



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "color")

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "color":
            kwargs["widget"] = TextInput(attrs={'type': 'color'})  # Використовуємо HTML віджет для вибору кольору
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(ProductOptionGroup)
class ProductOptionGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("group", "value")


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
    ]

    list_display = ("name", "category", "price")

    search_fields = ("id", "name","category__name")

    readonly_fields = ()


class OrderOptionPartInline(admin.TabularInline):
    model = OrderOptionsProductPart
    extra = 1


@admin.register(OrderProductPart)
class OrderPartAdmin(admin.ModelAdmin):
    inlines = [OrderOptionPartInline]



# Order and OrderPart Models Configuration
class OrderPartInline(admin.TabularInline):
    model = OrderProductPart
    extra = 1

    def render_options(self, obj):
        options = obj.options_order.all()
        if not options:
            return "No options available"
            # Формуємо HTML список
        options_list = "<ul>"
        for option in options:
            options_list += f"<li>fff{str(option)}</li>"
        options_list += "</ul>"
        return mark_safe(options_list)

    readonly_fields = ('render_options',)
    fields = ('render_options', 'product', 'count')
    render_options.short_description = "Order Options"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("datetime", "pib")
    inlines = [OrderPartInline]