from django.contrib import admin
from django.forms import TextInput

from .models import Category, ProductImage, ProductOption, Product, OrderProductPart, Order, Color, \
    ProductOptionGroup, OrderOptionsProductPart


class ProductInline(admin.TabularInline):
    model = Product
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

    list_display = ("name", "category", "get_min_full_price", "view_count", "purchase_count",)

    search_fields = ("id", "name","category__name",)

    readonly_fields = ("view_count", "purchase_count", "get_min_full_price")

    fields = (("view_count", "purchase_count","get_min_full_price"),"name", "category",("price","photo"),"description")

    ordering = ("view_count", "purchase_count", "price",)


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