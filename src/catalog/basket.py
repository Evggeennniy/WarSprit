import os

from .models import ProductOption, Product


def calculate_total_price(product_data):
    products = Product.objects.all()
    total_price = 0
    DISCOUNT = 0

    print(product_data)
    for product_info in product_data:
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


    if total_price != 0:
        DISCOUNT = os.getenv("DISCOUNT")
        if DISCOUNT:
            DISCOUNT = 150

    sumPrice = total_price - DISCOUNT

    if sumPrice < 0:
        sumPrice = 0



    return {
        "sumPrice": sumPrice,
        "sumPriceNoDiscount": total_price,
        "sumDiscountProduct": - DISCOUNT
    }

