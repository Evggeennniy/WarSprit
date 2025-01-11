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
    template_name = "product.html"
    context_object_name = "product"

    def get_queryset(self):
        return Product.objects.prefetch_related(
            'images',
            'options',
            'options__color',
            'options__group',
        )

    def get_top_products(self):
        """Метод для отримання 4 найбільш покупних товарів"""
        return Product.objects.order_by('-purchase_count')[:4]

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.increment_view_count()

        # Отримати топ-4 продукти через окремий метод
        top_products = self.get_top_products()

        context = self.get_context_data(object=self.object)
        context['top_products'] = top_products

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
