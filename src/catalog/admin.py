from django.contrib import admin
from django.forms import TextInput
from django.utils.safestring import mark_safe

from .models import Category, ProductImage, ProductOption, Product, OrderProductPart, Order, Color, \
    ProductOptionGroup, OrderOptionsProductPart


class ProductInline(admin.TabularInline):
    model = Product
    fields = ("mini_photo", "name", "price", "get_min_full_price", "view_count", "purchase_count")
    readonly_fields = ("view_count", "purchase_count", "get_min_full_price", "mini_photo")
    extra = 0


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("name",)

    search_fields = ("id", "name")

    readonly_fields = ()
    inlines = [
        ProductInline,
    ]


class ProductProductOption(admin.TabularInline):
    model = ProductOption
    extra = 0

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image", "mini_photo",)
    readonly_fields = ("mini_photo",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("colored_name",)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "color":
            kwargs["widget"] = TextInput(attrs={'type': 'color'})  # Використовуємо HTML віджет для вибору кольору
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(ProductOptionGroup)
class ProductOptionGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    inlines = [
        ProductProductOption,
        ProductImageInline
    ]

    list_display = ("name","mini_photo", "category", "get_min_full_price", "view_count", "purchase_count")

    search_fields = ("id", "name","category__name",)

    readonly_fields = ("mini_photo", "view_count", "purchase_count", "get_min_full_price", "big_photo")

    fields = (("view_count", "purchase_count","get_min_full_price"),"name", "category", "price", "description","photo", "big_photo")

    ordering = ("view_count", "purchase_count", "price",)

    @admin.display(description="photo")
    def big_photo(self, odj):
        return mark_safe(f"<a target='_blank' href='{odj.photo.url}'><img src='{odj.photo.url}' width=500></a>")


class OrderOptionPartInline(admin.TabularInline):
    model = OrderOptionsProductPart
    extra = 0


@admin.register(OrderProductPart)
class OrderPartAdmin(admin.ModelAdmin):
    inlines = [OrderOptionPartInline]


class OrderPartInline(admin.TabularInline):
    model = OrderProductPart
    extra = 0
    empty_value_display = "-empty-"

    list_display = ("option_text", 'product', 'count')
    readonly_fields = ('option_text',)
    fields = ('option_text', 'product', 'count',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("datetime", "pib")
    inlines = [OrderPartInline]