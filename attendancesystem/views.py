from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from attendancesystem.serializers import UserSerializer


# Create your views here.
@api_view(['POST'])
def logout_view(request):
    user = request.user
    user.auth_token.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
def get_user_id(request):
    return Response(request.user.id)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
def get_user_info(request):
    user = request.user
    serializer = UserSerializer(instance=user)
    return Response(serializer.data)