from django.contrib import admin
from django.forms import TextInput

from .models import Category, ProductImage, ProductOption, Product, OrderProductPart, Order, Color, \
    ProductOptionGroup


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


# Order and OrderPart Models Configuration
class OrderPartInline(admin.TabularInline):
    model = OrderProductPart
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("datetime", "pib")
    inlines = [OrderPartInline]