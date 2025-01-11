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

@admin.register(ProductOption)
class ProductOptionAdmin(admin.ModelAdmin):
    list_display = ("group", "format_html_value")


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    inlines = [
        ProductImageInline,
    ]

    list_display = ("name", "category", "price", "view_count", "purchase_count",)

    search_fields = ("id", "name","category__name",)

    readonly_fields = ("view_count", "purchase_count",)

    ordering = ("view_count", "purchase_count", "price")


class OrderOptionPartInline(admin.TabularInline):
    model = OrderOptionsProductPart
    extra = 0


@admin.register(OrderProductPart)
class OrderPartAdmin(admin.ModelAdmin):
    inlines = [OrderOptionPartInline]



# Order and OrderPart Models Configuration
class OrderPartInline(admin.TabularInline):
    model = OrderProductPart
    extra = 0
    empty_value_display = "-empty-"

    @admin.display(description="Опцій")
    def view_options(self, obj):
        options = obj.options_order.all()
        if not options:
            return "No options available"
            # Формуємо HTML список
        options_list = "<ul>"
        for option in options:
            options_list += f"<li>fff{str(option)}</li>"
        options_list += "</ul>"
        return options_list

    list_display = ("view_options", 'product', 'count')
    readonly_fields = ('view_options',)
    fields = ('view_options', 'product', 'count',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("datetime", "pib")
    inlines = [OrderPartInline]