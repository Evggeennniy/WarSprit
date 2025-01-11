from django.core.serializers import json
from django.http import JsonResponse
from django.views.generic import TemplateView, DetailView
import json

from .basket import calculate_total_price
from .models import Product, Category, Order, OrderProductPart, OrderOptionsProductPart
from .utils import send_telegram_message


class BasketView(TemplateView):
    template_name = "basket.html"


class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] =Category.objects.prefetch_related(
            "products"
        )
        return context


class ProductDetailsView(DetailView):
    model = Product
    template_name = "detail.html"
    context_object_name = "product"

    def get_top_products(self):
        """Метод для отримання 4 найбільш покупних товарів."""
        return Product.objects.order_by('-purchase_count')[:4]

    def get_surrounding_products(self, current_product):
        """Знайти попередній та наступний продукт за категорією з циклічним переходом."""
        category = current_product.category

        # Усі продукти в категорії, відсортовані за кількістю переглядів
        products_in_category = Product.objects.filter(category=category).order_by('-view_count', '-pk')

        # Якщо категорія порожня, повертаємо None
        if not products_in_category.exists():
            return None, None

        # Перетворюємо QuerySet на список
        products = list(products_in_category)

        # Знаходимо індекс поточного продукту
        current_index = next((i for i, product in enumerate(products) if product.pk == current_product.pk), None)

        # Визначаємо попередній та наступний продукти (циклічно)
        previous_product = products[current_index - 1] if current_index > 0 else products[-1]
        next_product = products[current_index + 1] if current_index < len(products) - 1 else products[0]

        # Повертаємо їхні ID
        return previous_product.pk, next_product.pk

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.increment_view_count()

        # Отримати топ-4 продукти через окремий метод
        top_products = self.get_top_products()

        # Отримати попередній і наступний продукти (тільки ID)
        previous_product_id, next_product_id = self.get_surrounding_products(self.object)

        context = self.get_context_data(object=self.object)
        context['top_products'] = top_products
        context['previous_product_id'] = previous_product_id
        context['next_product_id'] = next_product_id

        return self.render_to_response(context)


def basket(request):
    try:
        if request.method == "POST":
            body = json.loads(request.body)
            order_list = body.get("order_list")
            return JsonResponse({"status": "success", "data": calculate_total_price(order_list)})
        else:
            return JsonResponse({"error": "Invalid request"}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Invalid request"}, status=400)

def order_submit(request):
    if request.method == "POST":
        data = json.loads(request.body)
        pib = data.get("pib")
        phone = data.get("phone")
        city = data.get("city")
        post_office_id = data.get("postOfficeId")
        post_office = data.get("postOffice")
        order_content = data.get("order_list")
        result = calculate_total_price(order_content)
        full_price = result["sumPrice"]
        order = Order.objects.create(
            pib = pib,
            phone = phone,
            city = city,
            post_office_id = post_office_id,
            post_office =post_office,
            full_price = full_price
        )
        for product in order_content:
            obj = OrderProductPart.objects.create(
                count = product["productQuantity"],
                product_id = product["productId"],
                related_order = order,
            )
            options = [ OrderOptionsProductPart.objects.create(order_part = obj, option_id= option_id ) for option_id in  product["options"] ]

        send_telegram_message(order.get_telegram_text())
        return JsonResponse(
            {"status": "success"}
        )
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
