from django.shortcuts import render

def hello_world(request):
    return render(request, 'hello/hello_world.html')# Create your views here.