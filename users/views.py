from django.http import HttpResponse
from rest_framework import generics, permissions

from users.models import TblUser
from users.serializers import RegisterSerializer, UserProfileSerializer


# Create your views here.
def index(request):
    return HttpResponse("""
        <div style="height:100vh;display:flex;justify-content:center;align-items:center;background-color:black;color:white;font-weight:normal;font-size:50px;">
            <b>Your API Server is working!</b>
        </div>
    """)


class RegisterView(generics.CreateAPIView):
    queryset = TblUser.objects.all()
    serializer_class = RegisterSerializer


class UserDetailView(generics.RetrieveAPIView):
    queryset = TblUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)
