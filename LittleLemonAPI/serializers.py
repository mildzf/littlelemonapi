from rest_framework import serializers 
from rest_framework.validators import UniqueTogetherValidator
from django.contrib.auth.models import Group, User


from .models import Cart, Category, MenuItem, Order, OrderItem


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User 
        fields = ['id', 'username', 'email']


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = MenuItem 
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1 


class CartSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField(method_name='calculate_price')

    class Meta:
        model = Cart 
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
        

    def calculate_price(self, product:Cart):
        return product.unit_price * product.quantity
    
    def create(self, validated_data):
        # Calculate the price before creating the Cart item
        validated_data['unit_price'] = validated_data['menuitem'].price
        validated_data['price'] = validated_data['unit_price'] * validated_data['quantity']

        # Call the create method of the parent class
        return super().create(validated_data)
    



class OrderSerializer(serializers.ModelSerializer):
    delivery_crew = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order 
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem 
        fields = "__all__"