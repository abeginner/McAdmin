import json

from django.views.generic.base import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from McAdmin.mcadmin.models import *

class ServerView(View):
    
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        
        