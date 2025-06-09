from django.shortcuts import render, redirect
from .models import Note

def index(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Note.objects.create(content=content)
            return redirect('index')
    notes = Note.objects.all().order_by('-created_at')
    return render(request, 'index/index.html', {'notes': notes})

def charts(request):
    return render(request, 'index/charts.html')