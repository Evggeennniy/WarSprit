from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from colorfield.fields import ColorField

class Category(models.Model):
    name = models.CharField(verbose_name="Назва", max_length=16)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

class ProductOptionGroup(models.Model):
    name = models.CharField(verbose_name="Назва групи",max_length=64)

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

    class Meta:
        verbose_name = "Колір"
        verbose_name_plural = "Кольори"


class Prefix(models.Model):
    name = models.CharField(verbose_name="Префікс", max_length=10, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Префікс"
        verbose_name_plural = "Префікси"

class ProductOption(models.Model):
    group = models.ForeignKey(ProductOptionGroup, verbose_name="Група", on_delete=models.CASCADE, related_name="options"
    )
    color = models.ForeignKey(
        Color, verbose_name="Колір", on_delete=models.CASCADE, related_name="options",blank=True, null=True )

    prefix = models.ForeignKey(
        Prefix, on_delete=models.CASCADE, related_name="options", verbose_name="Префікс",blank=True, null=True
    )
    additional_price = models.IntegerField(verbose_name="Додаткова ціна опцій", default=0)
    value = models.CharField(verbose_name="Назва опції", max_length=64)

    def get_group(self):
        return self.group.name

    def get_color(self):
        if self.color:
            return self.color.color  # type: ignore

    def get_prefix(self):
        if self.prefix:
            return self.prefix.name # type: ignore


    def __str__(self) -> str:
        return "Варіант різновиду"

    class Meta:
        verbose_name = "Опцiя різновиду"
        verbose_name_plural = "Опцiї різновидiв"


class Product(models.Model):
    name = models.CharField(verbose_name="Назва", max_length=64)
    description = CKEditor5Field(
        verbose_name="Опис", config_name="default", max_length=2048
    )
    options = models.ManyToManyField(ProductOption, related_name="products", blank=True)
    category = models.ForeignKey(
        verbose_name="Категорiя",
        to=Category,
        on_delete=models.CASCADE,
        related_name="products",
    )
    included_in_block_buy= models.BooleanField(
        verbose_name="Включений у `З цим купують`", default=False
    )
    photo = models.ImageField(verbose_name="Головне фото", upload_to="images")
    price = models.IntegerField(verbose_name="Цiна")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"

    def get_telegram_text(self):
        return self.name


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


class OrderOptionsProductPart(models.Model):
    order_part = models.ForeignKey(
        verbose_name="Відношення до Продукту",
        to=OrderProductPart,
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    group = models.ForeignKey(ProductOptionGroup, verbose_name="Група", on_delete=models.CASCADE, related_name="options_group_order"
                              )
    option = models.ForeignKey(ProductOption, verbose_name="Група", on_delete=models.CASCADE, related_name="options_order"
                              )
    def __str__(self) -> str:
        return f"{self.group.name}-{self.option.name}"

    class Meta:
        verbose_name = "Обрана опція по продукту"
        verbose_name_plural = "Подробицi замовлень"

    def get_telegram_text(self):
        """
        Формує красивий текст для однієї частини замовлення.
        """

        return ""