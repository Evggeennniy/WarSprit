from django.contrib import admin
from django.forms import TextInput
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .icon import LINK_EDIT_ICON
from .models import Category, ProductImage, ProductOption, Product, OrderProductPart, Order, Color, \
    ProductOptionGroup, OrderOptionsProductPart


class ProductInline(admin.TabularInline):
    model = Product
    fields = ("admin_link_icon", "mini_photo", "name", "price", "get_min_full_price", "view_count", "purchase_count")
    readonly_fields = ("admin_link_icon", "view_count", "purchase_count", "get_min_full_price", "mini_photo")
    extra = 0


    @admin.display(description="Детальніше")
    def admin_link_icon(self, obj):
        """Додає іконку зі посиланням на редагування об’єкта."""
        url = reverse('admin:catalog_product_change', args=[obj.pk])
        return format_html(
            LINK_EDIT_ICON,url)


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ("name",)

    search_fields = ("id", "name")

    readonly_fields = ()
    inlines = [
        ProductInline,
    ]


class ProductProductOption(admin.StackedInline):
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
    fields = ("name",)


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
    list_display = ("product__name", "count", "related_order__id", "product__category")
    search_fields = ("product__id", "related_order_id")
    readonly_fields = ("big_photo",)
    fields = ("product", "count", "related_order", "big_photo")

    @admin.display(description="photo")
    def big_photo(self, odj):
        return mark_safe(f"<a target='_blank' href='{odj.product.photo.url}'><img src='{odj.product.photo.url}' width=500></a>")


class OrderPartInline(admin.TabularInline):
    model = OrderProductPart
    extra = 0
    empty_value_display = "-empty-"
    readonly_fields = ('product_option', 'mini_photo','admin_link_icon')
    fields = ('admin_link_icon', 'product', 'count', 'product_option','mini_photo')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("pib", "full_price", "datetime")
    inlines = [OrderPartInline]