from .models import Product
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from rest_framework.decorators import api_view, permission_classes
from .serializer import ProductSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied

#========================================
# task is :
    # 1- an api to get all products and create a new one
    # 2- an api to get/update/delete a single product
    # 3- only authenticated users can update/delete a product
    # 4- each user can only update/delete the products that
        # he/she has created

# all sections are doing the same thing, but with a different approach
#====================================================================


#--------------------------------------------------------------------
# to paginate
class ProductsPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


# to get products unauthorized and create one item authorized

#--------------------------------------------------------------------
# function based view

# to get all products and create new one :
@api_view(['get', 'POST'])
@permission_classes([IsAuthenticatedOrReadOnly])
def fbv_products(request: Request):
    if request.method == 'GET':
        # pagination :
        items = Product.objects.all()
        paginator = ProductsPagination()
        paginated_items = paginator.paginate_queryset(items, request)
        # get all products :
        serializer = ProductSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)

    elif request.method == 'POST':
        user = request.user
        deserializer = ProductSerializer(data=request.data, context={'user': user})
        if deserializer.is_valid():
            deserializer.save()
            return Response(deserializer.data, status.HTTP_201_CREATED)
        return Response(deserializer.errors, status.HTTP_400_BAD_REQUEST)

    return Response(None, status.HTTP_400_BAD_REQUEST)


# .....................................
# to get a single product by id and update/delete it
# only authenticated users can update/delete a product
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly])
def fbv_product_detail(request: Request, product_id):
    # to retrieve a product from DB :
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise NotFound()

    if request.method == 'GET':
        serializer = ProductSerializer(instance=product)
        return Response(serializer.data, status.HTTP_200_OK)

    # to update a product :
    elif request.method == 'PUT':
        # pass the current-user to serializer for validation
        serializer = ProductSerializer(instance=product, data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if product.created_by != request.user:
            raise PermissionDenied()
        product.delete()
        return Response(None, status.HTTP_204_NO_CONTENT)

    else:
        return Response(None, status.HTTP_400_BAD_REQUEST)


#--------------------------------------------------------------------
# class based view ( APIView )

# to get all products and create new one :
class ProductsAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request):
        items = Product.objects.all()
        paginator = ProductsPagination()
        paginated_items = paginator.paginate_queryset(items, request)
        serializer = ProductSerializer(paginated_items, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request):
        user = request.user
        deserializer = ProductSerializer(data=request.data, context={'user': user})
        if deserializer.is_valid():
            deserializer.save()
            return Response(deserializer.data, status.HTTP_201_CREATED)
        return Response(deserializer.errors, status.HTTP_400_BAD_REQUEST)


# .....................................
# to get a single product by id and update/delete it
# only authenticated users can update/delete a product
class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_product(self, pk):
        # to retrieve a product from DB :
        try:
            product = Product.objects.get(id=pk)
            return product
        except Product.DoesNotExist:
            raise NotFound()

    def get(self, request: Request, pk):
        product = self.get_product(pk)
        serializer = ProductSerializer(instance=product)
        return Response(serializer.data, status.HTTP_200_OK)

    def put(self, request: Request, pk):
        product = self.get_product(pk)
        serializer = ProductSerializer(instance=product, data=request.data, context={'user': request.user})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request: Request, pk):
        product = self.get_product(pk)
        if product.created_by != request.user:
            raise PermissionDenied()
        product.delete()
        return Response(None, status.HTTP_204_NO_CONTENT)


#--------------------------------------------------------------------
# class based view ( mixin )

# to get all products and create new one :
class ProductsMixinView(
    generics.GenericAPIView,
    mixins.ListModelMixin,
    mixins.CreateModelMixin
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request):
        return self.list(request)

    def post(self, request: Request):
        return self.create(request)

    # to pass current user to serializer for validation :
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


# .....................................
# to get a single product by id and update/delete it
# only authenticated users can update/delete a product
class ProductDetailMixinView(
    generics.GenericAPIView, mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin, mixins.DestroyModelMixin
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request: Request, pk):
        return self.retrieve(request, pk)

    def put(self, request: Request, pk):
        return self.update(request, pk)

    def delete(self, request: Request, pk):
        product = self.get_object()
        if product.created_by != request.user:
            raise PermissionDenied()
        return self.destroy(request, pk)

    # to pass current user to serializer for validation :
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


#--------------------------------------------------------------------
# class based view ( generics )

# to get all products and create new one :
class ProductsGenericView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    # to pass current user to serializer for validation :
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


#.....................................
# to get a single product by id and update/delete it
# only authenticated users can update/delete a product
class ProductDetailGenericView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductsPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    # to check that if current user is created the project
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        if product.created_by != request.user:
            raise PermissionDenied()
        return super().destroy(request, *args, **kwargs)

    # to pass current user to serializer for validation :
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


