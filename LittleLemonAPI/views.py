from rest_framework import viewsets, status, mixins, views
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User 
from django.shortcuts import get_object_or_404
from datetime import date 
from decimal import Decimal 

from .permissions import IsManagerOrAdmin, IsManagerOrSelfOrDeliveryCrew, IsManagerOrDeliveryCrew
from .models import Cart, MenuItem, Category, Order
from .serializers import (MenuItemSerializer, CartSerializer, CategorySerializer,
                           OrderSerializer, OrderItemSerializer)
from .mixins import ManagementMixin


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CategoryMenuItemsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MenuItemSerializer

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        return MenuItem.objects.filter(category_id=category_id)
    

class MenuItemsViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().select_related('category')
    serializer_class = MenuItemSerializer 

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return []
        return [IsAuthenticated(), IsManagerOrAdmin()]
    
 
    def create(self, request):
        """ Creates a menu item. """
        serialized_menuitem = MenuItemSerializer(data=request.data)
        if serialized_menuitem.is_valid():
            serialized_menuitem.save(category_id=request.data['category_id'])
            return Response(serialized_menuitem.data, status=status.HTTP_201_CREATED)
        return Response(serialized_menuitem.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, pk=None):
        """ Displays a single menu item. """
        menuitem = self.get_object()
        if menuitem:
            serialized_menuitem = MenuItemSerializer(menuitem)
            return Response(serialized_menuitem.data, status=status.HTTP_200_OK)
        return Response({"message":"Item not found"}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        """Updates a menu item."""
        menuitem = self.get_object()
        
        # Check if 'item_of_the_day' is present in the request data
        if 'featured' in request.data:
            # Remove 'item_of_the_day' from any other menu item
            item_of_the_day = MenuItem.objects.filter(featured=True).exclude(pk=menuitem.pk)
            item_of_the_day.update(featured=False)

            # Perform the update for the current menu item
            serialized_menuitem = MenuItemSerializer(menuitem, data=request.data, partial=True)
            if serialized_menuitem.is_valid():
                serialized_menuitem.save()
                return Response({"message": "Item updated successfully"}, status=status.HTTP_200_OK)
            return Response(serialized_menuitem.errors, status=status.HTTP_400_BAD_REQUEST)

        # If 'item_of_the_day' is not present, proceed with a normal update
        serialized_menuitem = MenuItemSerializer(menuitem, data=request.data)
        if serialized_menuitem.is_valid():
            serialized_menuitem.save()
            return Response({"message": "Item updated successfully"}, status=status.HTTP_200_OK)
        return Response(serialized_menuitem.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, pk=None):
        """ Deletes a menu item."""
        menuitem = self.get_object(pk)
        if menuitem:
            menuitem.delete()
            return Response({"message":"item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "item not found."}, status=status.HTTP_404_NOT_FOUND)


class ManagerViewSet(ManagementMixin):
    group_name = 'Manager'
    

class DeliveryCrewViewSet(ManagementMixin):
    group_name = 'Delivery_crew'
   

class CartViewSet(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()

    def list(self, request):
        """ Lists all cart items associated with the currently authenticated
        user. """
        cart_items = Cart.objects.filter(user=request.user)
        serialized_cart_items = CartSerializer(cart_items, many=True)
        return Response(serialized_cart_items.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Creates a cart item from menu item and assigns then current user to it."""
        menuitem_id = request.data.get('menuitem_id', None)
        quantity = request.data.get('quantity', None)

        if not (menuitem_id and quantity):
            return Response(
                {
                    "message":"Please ensure that both 'menuitem_id' \
                        and 'quantity' are present in your request"}, 
                        status=status.HTTP_400_BAD_REQUEST)
        try:
            menuitem = MenuItem.objects.get(pk=menuitem_id)
        except MenuItem.DoesNotExist():
            return Response({"message":"Menu item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("'quantity' must be a positive integer")
        except ValueError as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_data = {
            'user': request.user.pk,
            'menuitem':menuitem.id,
            'quantity':quantity,
            'unit_price': menuitem.price
        }

        cart_item = Cart.objects.filter(user=request.user, menuitem=menuitem).first()
        if cart_item:
            cart_item.quantity += int(quantity)  # if a cart item exist for same menu item and user, simply increment quantity
            cart_item.save()
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        serializer = CartSerializer(data=cart_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def retrieve(self, request, pk=None):
        """Returns the single cart item"""
        cart_item = Cart.objects.filter(user=request.user).filter(pk=pk).first()
        if cart_item:
            serializer = CartSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message":"Item not found"}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        """Deletes cart item"""
        cart = Cart.objects.filter(user=request.user).filter(pk=pk).first()
               
        if cart:
            cart.delete()
            return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        


class OrderViewSet(viewsets.ModelViewSet):

    def get_permissions(self):
        if self.action == 'partial_update':
            return [IsManagerOrDeliveryCrew()]
        elif self.action == 'list':
            return [IsManagerOrSelfOrDeliveryCrew()]
        return [IsAuthenticated()]

    def list(self, request, order_id=None): 
        """This method checks if the user is a manager then displays all orders.
        If the user is delivery crew it displays all orders assigned to that delivery
        crew."""
        orders = Order.objects.filter(user=request.user)
        if request.user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif request.user.groups.filter(name='Delivery_crew').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
    
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
        
    
    def retrieve(self, request, pk=None):
        """This method displays the order of the currently authenticated request user."""
        if pk is not None:
            order = get_object_or_404(Order, pk=pk)
            if order:
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        

        
    def create(self, request):
        """
        Creates an order and assigns the current authenticated user to that order. 
        The users cart items are used to create order items which are then associated
        with that order.
        """
        user = request.user

        # Initial data for order
        order_data = {
            'user': user.id,
            'delivery_crew': None,
            'status': 0,
            'total': Decimal('0.00'),  # Use Decimal for precision
            'date': date.today(),
        }

        order_serializer = OrderSerializer(data=order_data)
        if not order_serializer.is_valid():
            return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_instance = order_serializer.save()

        cart_items = user.cart_set.all()
        order_items_data = []

        for item in cart_items:
            order_item_data = {
                'order': order_instance.id,
                'menuitem': item.menuitem.id,
                'quantity': item.quantity,
                'unit_price': item.menuitem.price,
                'price': item.price,
            }
            order_items_data.append(order_item_data)

        order_items_serializer = OrderItemSerializer(data=order_items_data, many=True)
        if not order_items_serializer.is_valid():
            return Response(order_items_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        order_items_serializer.save()

        # Calculate total after adding all order items
        order_instance.total = sum(item.price for item in cart_items)
        order_instance.save()

        # Clear the cart
        user.cart_set.all().delete()

        response_data = {
            'order': OrderSerializer(order_instance).data,
            'order_items': OrderItemSerializer(order_instance.orderitem_set.all(), many=True).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)
    

    def partial_update(self, request, pk=None):
        """Allows the manager to assign the delivery crew and both manager and delivery
        crew to adjust order status."""
        order = get_object_or_404(Order, pk=pk)
        delivery_crew_id = request.data.get('username', None)
        status_value = request.data.get('status', 0)
        print("DEBUG: ", f"{request.user} - {request.user.groups.filter(name="Delivery_crew").exists()} --{request.data.get('status')}")

        if request.user.groups.filter(name='Manager').exists() and delivery_crew_id is not None:
            delivery_crew = get_object_or_404(User, username=delivery_crew_id)
            order.delivery_crew = delivery_crew
            order.save()
        elif request.user.groups.filter(name='Delivery_crew').exists():
            print("DEBUG: ", "Im in the delivery group")
            order.status = status_value
            order.save()
        else:
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)




    

























