from django.core.serializers import json
from django.http import JsonResponse
from django.views.generic import TemplateView, DetailView

from .models import Product, Category, Order
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
def basket(request):
    try:
        if request.method == "POST":
            order_list = json.loads(request.body).get("order_list")


            return JsonResponse({"status": "success", "data": order_list})
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
        result = basket.calculate_basket(
            data.get("order_list"), data.get("promocodeName")
        )
        order_content = data.get("order_list")
        full_price = result["sumPrice"]
        order = Order.objects.create(
            pib = pib,
            phone = phone,
            city = city,
            post_office_id = post_office_id,
            post_office =post_office
        )
        """
        order_content = [
            catalog_models.OrderPart.objects.create(
                related_order=order,
                product=catalog_models.Product.objects.filter(
                    id=item.get("productId")
                ).first(),
                count=item.get("productQuantity"),
                volume=catalog_models.ProductVolume.objects.filter(
                    id=item.get("volumeId")
                ).first(),
                wrapper=catalog_models.ProductWrapper.objects.filter(
                    id=item.get("wrapperId")
                ).first(),
            )
            for item in order_content
        ]
        """
        send_telegram_message(order.get_telegram_text())
        return JsonResponse(
            {"status": "success"}
        )
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)
