from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated , AllowAny
from .serializers import LoginSerializer,RegisterSerializer


class LoginView(APIView):
    
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self,request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'access':str(refresh.access_token),
                'refresh': str(refresh)
            }
        )
    
class RegisterView(APIView):
    permission_classes=[AllowAny]
    authentication_classes=[]
    def post(self,request):

        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'status':201,
                'access':str(refresh.access_token),
                'refresh': str( refresh)

            }
        )
    
class LogoutView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        try:
            refresh_token = request.data['refresh']
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except Exception:
            return Response(status=400)