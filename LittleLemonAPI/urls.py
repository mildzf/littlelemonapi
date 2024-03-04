from django.urls import include, path 
from rest_framework.routers import DefaultRouter

from . import views 

router = DefaultRouter(trailing_slash=False)
router.register('categories', views.CategoryViewSet, basename='category')
router.register('categories/<int:pk>', views.CategoryMenuItemsViewSet, basename='category-menuitems')
router.register('menu-items', views.MenuItemsViewSet, basename='menuitem')
router.register('groups/managers/users', views.ManagerViewSet, basename='manager')
router.register('groups/delivery-crew/users', views.DeliveryCrewViewSet, basename='delivery-crew')
router.register('cart/menu-items', views.CartViewSet, basename='cart')
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls))
]





# urlpatterns = [
#     path('categories', views.CategoryViewSet.as_view({
#         'get':'list',
#         'post':'create'
#     })),
#     path('categories/<int:category_id>/menu-items/', views.CategoryMenuItemsViewSet.as_view({
#         'get': 'list'
#         })),
#     path('menu-items', views.MenuItemsViewSet.as_view({
#         'get':'list',
#         'post':'create'
#     })),
#     path('menu-item/<int:pk>', views.MenuItemsViewSet.as_view({
#         'get': 'retrieve',
#         'delete':'destroy',
#         'put': 'update',
#         'patch':'update'
#     })),
#     path('groups/managers/users', views.ManagerViewSet.as_view({
#         'get':'list',
#         'post': 'create',
#     })),
#     path('groups/managers/users/<int:pk>', views.ManagerViewSet.as_view({
#         'post':'destroy',
#         'delete':'destroy',
#     })),
#     path('groups/delivery-crew/users', views.DeliveryCrewViewSet.as_view({
#         'get':'list',
#         'post':'create',
#     })),
#     path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewViewSet.as_view({
#         'post':'destroy',
#         'delete':'destroy',
#     })),
#     path('cart/menu-items', views.CartViewSet.as_view({
#         'get':'list',
#         'post':'create',
        
#     })),
# path('cart/menu-items/<int:pk>',views.CartViewSet.as_view({
#     'get':'retrieve',
#     'delete':'destroy'
# })),
# path('orders', views.OrderViewSet.as_view()),
# path('orders/<int:order_id>', views.OrderViewSet.as_view())
# ]