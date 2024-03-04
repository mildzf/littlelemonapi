# @api_view(['POST', 'DELETE']) 
# @permission_classes([IsManagerOrAdmin]) 
# def delivery_crew(request, pk=None):
#     username = request.data['username']
#     delivery_crew = Group.objects.get(name='Delivery_crew')
#     user_id = request.GET.get('pk')
#     if request.method == 'GET':
#         serialized_group = GroupSerializer(delivery_crew)
#         return Response(serialized_group.data, status=status.HTTP_200_OK)
#     if username:
#         user = get_object_or_404(User, username=username)
#         if request.method=='POST':
#             delivery_crew.user_set.add(user)
#             return Response({"message":"Success!"}, status=status.HTTP_201_CREATED)
#     elif user_id:
#         if request.method=='DELETE':
#             managers.user_set.remove(user)
#             return Response({"message": "Success!"}, status=status.HTTP_200_OK)
#     return Response(request, status=status.HTTP_404_NOT_FOUND)



# @api_view(['POST','DELETE'])
# @permission_classes([IsManagerOrAdmin])
# def managers(request, pk=None):
#     username = request.data['username']
#     user_id = request.GET.get('pk')
#     managers = Group.objects.get(name='Manager')
#     if request.method == 'GET':
#         serialized_group = GroupSerializer(managers)
#         return Response(serialized_group.data, status=status.HTTP_200_OK)
#     if username:
#         user = get_object_or_404(User, username=username)
#         if request.method=='POST':
#             managers.user_set.add(user)
#             return Response(request, status=status.HTTP_201_CREATED)
#     elif user_id:
#         if request.method=='DELETE':
#             managers.user_set.remove(user)
#             return Response({"message": "Success!"}, status=status.HTTP_200_OK)
#     return Response({"message":"User not found!"}, status=status.HTTP_404_NOT_FOUND)