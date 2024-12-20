from django.urls import path
from . import views

# ========================================
# each seperated part doing the same thing
    # first one is to get all products and create a new one
    # second one is for get/update/delete a single product
# ====================================================================

urlpatterns = [
    # function based view :
    path('fbv', views.fbv_products),
    path('fbv/<product_id>', views.fbv_product_detail),

    # APIView :
    path('api-view', views.ProductsAPIView.as_view()),
    path('api-view/<pk>', views.ProductDetailAPIView.as_view()),

    # Mixins :
    path('mixin', views.ProductsMixinView.as_view()),
    path('mixin/<pk>', views.ProductDetailMixinView.as_view()),

    # Generics :
    path('generic', views.ProductsGenericView.as_view()),
    path('generic/<pk>', views.ProductDetailGenericView.as_view()),
]
