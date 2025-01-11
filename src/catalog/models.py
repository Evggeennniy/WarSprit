from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from colorfield.fields import ColorField
from django_ckeditor_5.fields import CKEditor5Field


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


class ProductOption(models.Model):
    group = models.ForeignKey(ProductOptionGroup, verbose_name="Група", on_delete=models.CASCADE, related_name="options"
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
        return  f"{self.group.name}-{self.value}-{self.additional_price}₴" if self.additional_price else f"{self.group.name}-{self.value}"

    class Meta:
        verbose_name = "Опцiя різновиду"
        verbose_name_plural = "Опцiї різновидiв"


class Product(models.Model):
    name = models.CharField(verbose_name="Назва", max_length=64)
    description = models.TextField(verbose_name="Опис")
    options = models.ManyToManyField(ProductOption, related_name="products", blank=True)
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

    def get_telegram_text(self):
        order_parts = self.order_items.all()
        parts_text = "\n".join([part.get_telegram_text() for part in order_parts])

        return (
            f"Дата та час замовлення: {self.datetime.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"🛒 Замовлення №{self.id} від {self.pib}:\n"
            f"Номер телефону: +{self.phone}\n"
            f"Місто: {self.city}\n"
            f"Пошта: {self.post_office}/{self.post_office_id}\n"
            "📦 Товари:\n\n"
            f"{parts_text}"
            f"Всього: {self.full_price} ₴\n"
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
        return ""

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
        related_name="order_items",
    )
    option = models.ForeignKey(ProductOption, verbose_name="Група", on_delete=models.CASCADE, related_name="options_order"
                              )
    def __str__(self) -> str:
        return f"{self.option.group.name}-{self.option.value}-{self.option.additional_price}₴" if self.option.additional_price else f"{self.option.group.name}-{self.option.value}"


    class Meta:
        verbose_name = "Обрана опція по продукту"
        verbose_name_plural = "Подробицi замовлень"

    def get_telegram_text(self):
        """
        Формує красивий текст для однієї частини замовлення.
        """

        return ""