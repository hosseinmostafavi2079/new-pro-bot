from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, SystemSettingSerializer
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SystemSetting

# ویوی لاگین اختصاصی
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,) # همه بتوانند ثبت‌نام کنند
    serializer_class = UserSerializer

# ویوی تنظیمات سیستم
class SystemSettingView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        setting, _ = SystemSetting.objects.get_or_create(id=1)
        serializer = SystemSettingSerializer(setting)
        return Response(serializer.data)

    def put(self, request):
        setting, _ = SystemSetting.objects.get_or_create(id=1)
        serializer = SystemSettingSerializer(setting, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)