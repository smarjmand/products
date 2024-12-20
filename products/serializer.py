from rest_framework import serializers
from .models import Product


#--------------------------------------------------------------------
# to serialize/deserialize products :
class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at']

    # to check if current-user is the one who created the product or not:
    def validate(self, attrs):
        owner = self.instance.created_by
        user = self.context.get('user')
        name = attrs.get('name')
        price = int(attrs.get('price'))

        if owner != user:
            raise serializers.ValidationError(
                {'detail': 'شما مجاز به انجام این عملیات نیستید'},
                code='permission_denied'
            )

        elif Product.objects.filter(name=name).exists():
            raise serializers.ValidationError('این محصول قبلا ثبت شده است')

        elif price < 0:
            raise serializers.ValidationError('قیمت محصول نمی تواند عددی منفی باشد')

        return attrs

    # to add the user to product :
    def create(self, validated_data):
        validated_data['created_by'] = self.context['user']
        return Product.objects.create(**validated_data)
