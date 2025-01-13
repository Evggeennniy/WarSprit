from django.contrib import admin
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from colorfield.fields import ColorField
from django.utils.safestring import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from .icon import LINK_EDIT_ICON


class Category(models.Model):
    name = models.CharField(verbose_name="Назва", max_length=16)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

class ProductOptionGroup(models.Model):
    name = models.CharField(verbose_name="Назва групи",max_length=64)
    is_required = models.BooleanField(verbose_name="Обов'язкова група", default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Група опцій різновиду"
        verbose_name_plural = "Групи опцiї різновидів"

class Color(models.Model):
    name = models.CharField(verbose_name="Назва кольору", max_length=20, unique=True)
    color = ColorField(verbose_name="Колір", default='#FF0000')

    def __str__(self):
        return self.name

    @admin.display(ordering="name")
    def colored_name(self):
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color,
            self.name,
        )

    class Meta:
        verbose_name = "Колір опцiй"
        verbose_name_plural = "Коліри опцiй"

class Product(models.Model):
    name = models.CharField(verbose_name="Назва", max_length=64)
    description = models.TextField(verbose_name="Опис")
    category = models.ForeignKey(
        verbose_name="Категорiя",
        to=Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    photo = models.ImageField(verbose_name="Головне фото", upload_to="images")
    price = models.PositiveIntegerField(verbose_name="Цiна")
    purchase_count = models.PositiveIntegerField(
        verbose_name="Кількість покупок", default=0
    )

    view_count = models.PositiveIntegerField(
        verbose_name="Кількість переглядів", default=0
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def get_telegram_text(self):
        return self.name

    def increment_view_count(self):
        """Збільшити кількість переглядів на 1."""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    @admin.display(description="photo")
    def mini_photo(self):
        return mark_safe(f"<a target='_blank' href='{self.photo.url}'><img src='{self.photo.url}' width=70></a>")

    @admin.display(description="Мінімальна ціна товара з опціями")
    def get_min_full_price(self):
        """Calculate the minimum full price by adding the cheapest option from each group."""
        # Get all unique groups associated with the product via the options
        groups = ProductOptionGroup.objects.filter(options__product=self).distinct()

        # Initialize the total minimum price with the base price
        min_price = self.price

        # Iterate over each group to find the cheapest option in that group
        for group in groups:
            # Filter options for the current product and group, and get the minimum additional price
            min_additional_price = group.options.filter(product=self).order_by(
                'additional_price').first().additional_price
            min_price += min_additional_price

        return min_price

class ProductOption(models.Model):
    group = models.ForeignKey(ProductOptionGroup, verbose_name="Група", on_delete=models.CASCADE, related_name="options"
    )
    product = models.ForeignKey(Product, verbose_name="Продукт", on_delete=models.CASCADE, related_name="options"
    )
    color = models.ForeignKey(
        Color, verbose_name="Колір", on_delete=models.CASCADE, related_name="options",blank=True, null=True )

    additional_price = models.IntegerField(verbose_name="Додаткова вартість", default=0)
    value = CKEditor5Field(
        verbose_name="Назва опцій", max_length=100, config_name="default"
    )

    def get_group(self):
        return self.group.name

    def get_color(self):
        if self.color:
            return self.color.color  # type: ignore

    @admin.display(ordering="value")
    def format_html_value(self):
        return format_html(self.value)

    def __str__(self) -> str:
        return  f"{self.group.name}-{format_html(self.value)}-{self.additional_price}₴" if self.additional_price else f"{self.group.name}-{format_html(self.value)}"

    class Meta:
        verbose_name = "Опцiя різновиду"
        verbose_name_plural = "Опцiї різновидiв"


class ProductImage(models.Model):
    image = models.FileField(verbose_name="Зображення", upload_to="images")
    product = models.ForeignKey(
        verbose_name="Відноситься до",
        to=Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    def __str__(self) -> str:
        return "Зображення товару"

    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарiв"

    @admin.display(description="photo")
    def mini_photo(self):
        return mark_safe(f"<a target='_blank' href='{self.image.url}'><img src='{self.image.url}' width=70></a>")


class Order(models.Model):
    datetime = models.DateTimeField(
        verbose_name="Дата та час замовлення", auto_now_add=True
    )
    pib = models.CharField(verbose_name="ПІБ", max_length=512)
    phone = models.CharField(verbose_name="Номер Телефона", max_length=16)
    city = models.CharField(verbose_name="Місто", max_length=200)
    post_office = models.CharField(verbose_name="Пошта", max_length=100)
    post_office_id = models.CharField(verbose_name="Вiддiлення", max_length=100)
    full_price = models.DecimalField(
        verbose_name="Цiна", max_digits=12, decimal_places=2
    )
    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self) -> str:
        return f"№{self.id} {self.pib}"

    def get_telegram_text(self):
        order_parts = self.order_items.all()
        parts_text = "\n".join([part.get_telegram_text() for part in order_parts])

        return (
            f"📌№{self.id}|Дата та час замовлення: {self.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🛒 Замовлення №{self.id} від {self.pib}:\n"
            f"📞Номер телефону: +{self.phone}\n"
            f"🏢Місто: {self.city}\n"
            f"📦Пошта: {self.post_office}|{self.post_office_id}\n"
            "🛍Товари:\n\n"
            f"{parts_text}\n"
            f"💰Усього: {self.full_price} ₴\n"
        )


class OrderProductPart(models.Model):
    related_order = models.ForeignKey(
        verbose_name="Відношення до замовлення",
        to=Order,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    product = models.ForeignKey(
        verbose_name="Товар", to=Product, on_delete=models.SET_NULL, null=True
    )
    count = models.IntegerField(verbose_name="Кiлькiсть")

    class Meta:
        verbose_name = "Подробицi замовлення"
        verbose_name_plural = "Подробицi замовлень"

    def get_telegram_text(self):
        """
        Формує красивий текст для однієї частини замовлення.
        """

        option_items = self.option_items.all().order_by("option__group__id")
        elements = ["🔹", "🔸"]
        options_list = ""
        price= self.product.price
        element_index = 0
        for item in option_items:
            elem = elements[element_index % len(elements)]
            options_list += f"{elem}{item.get_telegram_text()}"
            price += item.option.additional_price
            element_index += 1
        price_text = f"{price}₴;"
        if self.count !=1:
            price_text = f"{self.count}шт.*{price}₴={self.count*price}₴"
        return (
            f"👕{self.product.id}|{self.product.name}\n"
            f"{options_list}"
            f"💵Ціна: {price_text}\n"
        )

    @admin.display(description="фото")
    def mini_photo(self):
        return self.product.mini_photo()


    @admin.display(description="Опцій ")
    def product_option(self):
        option_items = self.option_items.all()
        if not option_items:
            return "No options available"
            # Формуємо HTML список
        options_list=""
        for item in option_items:
            options_list += item.colored_name()
        return mark_safe(options_list)

    @admin.display(description="Детальніше")
    def admin_link_icon(self):
        """Додає іконку зі посиланням на редагування об’єкта."""
        url = reverse('admin:catalog_orderproductpart_change', args=[self.pk])
        return format_html(
            LINK_EDIT_ICON,url)

    def save(self, *args, **kwargs):
        """
        Перевизначення методу save для автоматичного оновлення purchase_count.
        """
        if self.pk is None and self.product:  # Перевіряємо, чи це новий запис
            self.product.purchase_count += self.count
            self.product.save(update_fields=["purchase_count"])
        super().save(*args, **kwargs)


class OrderOptionsProductPart(models.Model):
    order_part = models.ForeignKey(
        verbose_name="Відношення до Продукту",
        to=OrderProductPart,
        on_delete=models.CASCADE,
        related_name="option_items",
    )
    option = models.ForeignKey(ProductOption, verbose_name="Опція", on_delete=models.CASCADE, related_name="options_order"
                              )
    def __str__(self) -> str:
        return f"-{self.option.group.name}-{self.option.value} (+{self.option.additional_price}₴)" if self.option.additional_price else f"-{self.option.group.name}-{self.option.value}"

    def colored_name(self):
        if self.option.color:
            return f'<span style="color: {self.option.color.color}">{self.option.value}</span>'
        return self.option.value


    class Meta:
        verbose_name = "Опція по товару"
        verbose_name_plural = "Опцій по товару"

    def get_telegram_text(self):
        return f"{self.option.group.name}: {self.option.value}:{self.option.additional_price}₴\n" if self.option.additional_price else f"{self.option.group.name}:{self.option.value}\n"