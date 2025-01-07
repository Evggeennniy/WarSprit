from django.db.models import Prefetch

from .models import (
    FreeDeliveryPromotion,
    ProductVolume,
    ProductWrapper,
    Product,
    FreeProductPromotion,
    PriceDiscountPromotion,
    QuantityDiscountPromotion,
    Promocode,
)


class PromoDate:

    def __init__(self, order_parts, promo_code):
        print(order_parts)
        self.order_parts: list[dict[str, int | None | str]] = order_parts
        self.total_quantity: int = 0
        self.total_price: int = 0
        self.categories: dict[str, dict[str, int]] = {}
        self.discount: [dict[str, int]] = []
        self.labels: {str} = set()
        self.present: list[dict[str, int | None | str]] = []
        self.promo_code = promo_code
        self.promo_discount = 0
        self.promo_code_cof = 0

    def add_label(self, label: str):
        self.labels.add(label)

    def add_categories(self, name: str, cat_quantity, cat_price):
        self.total_quantity += cat_quantity
        if name in self.categories:
            self.categories[name]["total_quantity"] += cat_quantity
            self.categories[name]["total_price"] += cat_price
        else:
            self.categories[name] = {
                "total_quantity": cat_quantity,
                "total_price": cat_price,
            }

    def add_discount(self, name: str, value):
        not_found = True
        for item in self.discount:
            if item.get("name") == name:
                item["value"] += int(value)
                not_found = False
                break
        if not_found:
            self.discount.append({"name": name, "value": int(value)})

    def add_present(self, name: dict[str, int | None | str]):
        self.present.append(name)

    def apply_discount(self, sum_price):
        my_sum = sum_price - sum([dis["value"] for dis in self.discount])
        if self.promo_code:
            prom = Promocode.objects.get(name=self.promo_code)
            if prom:
                self.promo_code_cof = prom.discount
                self.promo_discount = my_sum * 0.01 * prom.discount
                self.add_discount(f"Промокод {self.promo_code}", self.promo_discount)
                return my_sum - self.promo_discount
        return my_sum

    def get_response(self):
        return {
            "promoCodeCof": self.promo_code_cof,
            "discountLabel": list(self.labels),
            "discount": list(
                map(lambda item: {**item, "value": item["value"] * -1}, self.discount)
            ),
            "presentList": self.present,
            "promoCodeDiscount": self.promo_discount * -1,
        }


def calculate_free_delivery(promo_date: PromoDate):
    # БЕЗКОШТОВНА ДОСТАВКА
    promotions = FreeDeliveryPromotion.objects.prefetch_related(
        "applicable_categories"
    ).all()
    for promo in promotions:
        applicable_category_ids = list(
            promo.applicable_categories.values_list("id", flat=True)
        )
        if applicable_category_ids:
            for category_id, category_data in promo_date.categories.items():
                if int(category_id) in applicable_category_ids:
                    if (
                        promo.promo_controller == "price"
                        and category_data["total_price"] >= promo.promo_value
                    ):
                        promo_date.add_label(promo.name)
                    elif (
                        promo.promo_controller == "count"
                        and category_data["total_quantity"] >= promo.promo_value
                    ):
                        promo_date.add_label(promo.name)
        else:
            if (
                promo.promo_controller == "price"
                and promo_date.total_price >= promo.promo_value
            ):
                promo_date.add_label(promo.name)
            elif (
                promo.promo_controller == "count"
                and promo_date.total_quantity >= promo.promo_value
            ):
                promo_date.add_label(promo.name)


def calculate_promo_present(promo_date: PromoDate) -> []:
    # ПОДАРУНКИ ЗА КОЖНУ КАТЕГОРІЮ
    promotions = FreeProductPromotion.objects.prefetch_related(
        "applicable_categories"
    ).all()
    for promo in promotions:
        applicable_category_ids = list(
            promo.applicable_categories.values_list("id", flat=True)
        )
        free_product_count = 0
        for category_id, category_data in promo_date.categories.items():
            if int(category_id) in applicable_category_ids:
                if category_data["total_quantity"] >= promo.promo_count:
                    applicable_times = (
                        category_data["total_quantity"] // promo.promo_count
                    )
                    free_product_count += applicable_times

        if (
            not applicable_category_ids
            and promo_date.total_quantity >= promo.promo_count
        ):
            applicable_times = promo_date.total_quantity // promo.promo_count
            free_product_count += applicable_times

        if free_product_count > 0:
            print(f"{free_product_count} x {promo.name}")
            order_par = get_cheapest_product_in_category(
                promo.promo_category.id, promo_date.order_parts
            )
            if order_par:
                promo_date.add_label(f"{free_product_count} x {promo.name}")
                order_par["productQuantity"] = free_product_count
                promo_date.add_present(order_par)


def calculate_quantity_price(promo_date: PromoDate) -> []:
    promotions = QuantityDiscountPromotion.objects.prefetch_related(
        Prefetch("applicable_categories")
    )
    for promo in promotions:
        applicable_category_ids = list(
            promo.applicable_categories.values_list("id", flat=True)
        )
        if applicable_category_ids:
            for category_id, category_data in promo_date.categories.items():
                if int(category_id) in applicable_category_ids:
                    if category_data["total_quantity"] >= promo.promo_quantity:
                        one_price = (
                            category_data["total_price"]
                            // category_data["total_quantity"]
                        )
                        quantity_active = (
                            category_data["total_quantity"] // promo.promo_quantity
                        )
                        promo_date.add_discount(
                            promo.name,
                            one_price * quantity_active * promo.promo_discount * 0.01,
                        )
                        promo_date.add_label(promo.name)
        else:
            if promo_date.total_price >= promo.promo_price:
                one_price = promo_date.total_price / promo_date.total_quantity
                quantity_active = promo_date.total_quantity // promo.promo_quantity
                promo_date.add_discount(
                    promo.name,
                    one_price * quantity_active * promo.promo_discount * 0.01,
                )
                promo_date.add_label(promo.name)


def calculate_promo_discount_sum(promo_date: PromoDate) -> []:
    promotions = PriceDiscountPromotion.objects.prefetch_related(
        Prefetch("applicable_categories")
    )
    for promo in promotions:
        applicable_category_ids = list(
            promo.applicable_categories.values_list("id", flat=True)
        )
        if applicable_category_ids:
            for category_id, category_data in promo_date.categories.items():
                if int(category_id) in applicable_category_ids:
                    if category_data["total_price"] >= promo.promo_price:
                        promo_date.add_discount(
                            promo.name,
                            category_data["total_price"] * promo.promo_discount / 100,
                        )
                        promo_date.add_label(promo.name)
        else:
            if promo_date.total_price >= promo.promo_price:
                promo_date.add_discount(
                    promo.name, promo_date.total_price * promo.promo_discount / 100
                )
                promo_date.add_label(promo.name)


def calculate_basket(order_parts: [], promo_code):
    sum_price_no_discount = 0
    wrapper_price = 0
    sum_discount_product = 0
    promo_date = PromoDate(order_parts, promo_code)
    for part in order_parts:
        volume = (
            ProductVolume.objects.get(id=part["volumeId"]) if part["volumeId"] else None
        )
        if part["wrapperId"]:
            wrapper = (
                ProductWrapper.objects.get(id=part["wrapperId"])
                if part["wrapperId"]
                else None
            )
            wrapper_price += int(wrapper.price) if wrapper else 0

        quantity = (
            int(part["productQuantity"])
            if isinstance(part["productQuantity"], str)
            else part["productQuantity"]
        )
        price = int(volume.price) if volume else 0
        discount = int(volume.discount) if volume else 0
        sum_price_no_discount += price * quantity
        sum_discount_product += price * quantity * discount / 100
        # promo
        product = Product.objects.get(id=part["productId"])
        promo_date.add_categories(
            str(product.related_category.id),
            quantity,
            sum_price_no_discount - sum_discount_product,
        )

    promo_date.total_price = (
        sum_price_no_discount - sum_discount_product
    )  # -wrapper_price
    sum_price = sum_price_no_discount - sum_discount_product + wrapper_price

    calculate_free_delivery(promo_date)
    calculate_promo_present(promo_date)
    calculate_promo_discount_sum(promo_date)
    calculate_quantity_price(promo_date)
    sum_price = promo_date.apply_discount(sum_price)
    return {
        **promo_date.get_response(),
        "sumPriceNoDiscount": sum_price_no_discount,
        "wrapperPrice": wrapper_price,
        "sumDiscountProduct": sum_discount_product * -1,
        "sumPrice": sum_price,
    }


def get_cheapest_product_in_category(category_id, product_params):
    products_in_category = Product.objects.filter(related_category_id=category_id)
    cheapest_product = None
    min_price = float("inf")

    for param in product_params:
        product_id = param["productId"]
        volume_id = param["volumeId"]
        wrapper_id = param["wrapperId"]

        try:
            product = products_in_category.get(id=product_id)
        except Product.DoesNotExist:
            continue

        try:
            volume = product.volumes.get(id=volume_id)
        except ProductVolume.DoesNotExist:
            continue

        curr_price = volume.get_curr_price()
        wrapper_price = 0
        if wrapper_id:
            try:
                wrapper = product.wrappers.get(id=wrapper_id)
                wrapper_price = wrapper.price
            except ProductWrapper.DoesNotExist:
                continue

        total_price = curr_price + wrapper_price

        if total_price < min_price:
            min_price = total_price
            cheapest_product = {
                "itemId": param.get("itemId"),
                "categoryId": str(category_id),
                "productId": str(product.id),
                "productImg": (
                    product.images.first().image.url
                    if product.images.exists()
                    else None
                ),
                "productName": product.name,
                "optionName": param.get("optionName"),
                "volume": volume.value,
                "volumeId": str(volume.id),
                "volumePrice": str(volume.price),
                "volumeDiscount": str(volume.discount),
                "wrapperName": wrapper.name if wrapper_id else None,
                "wrapperId": str(wrapper.id) if wrapper_id else None,
                "wrapperPrice": str(wrapper_price) if wrapper_id else None,
                "productQuantity": param.get("productQuantity", 1),
                "currentPrice": str(round(total_price, 2)),
            }

    return cheapest_product
