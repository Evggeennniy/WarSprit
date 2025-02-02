import os
from django.conf import settings
from .models import ProductOption, Product


def calculate_total_price(product_data):
    products = Product.objects.all()
    total_price = 0
    DISCOUNT = settings.DISCOUNT
    no_active_product = []

    for product_info in product_data:
        try:
            product_id = product_info["productId"]
            product_quantity = product_info["productQuantity"]
            options = product_info["options"]

            print(options)
            # Отримуємо продукт
            product = products.get(id=product_id)

            if product:
                # Базова ціна товару
                base_price = product.price

                # Додаткова вартість опцій
                additional_price = sum(
                    ProductOption.objects.get(id=option).additional_price
                    for option in options
                )

                # Загальна ціна для поточного товару
                total_price += (base_price + additional_price) * product_quantity
        except Product.DoesNotExist:
            no_active_product.append(product_info["productId"])
            print(no_active_product)


    sumPrice = total_price - DISCOUNT

    if sumPrice < 0:
        sumPrice = 0



    return {
        "sumPrice": sumPrice,
        "sumPriceNoDiscount": total_price,
        "sumDiscountProduct": - DISCOUNT,
        "deleteProductNoActive": no_active_product
    }

