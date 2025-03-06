from django.shortcuts import render

# Create your views here.
def index(request):
    context = {
        'index_text': "Welcome to index page.",
    }
    return render(request, 'index.html', context)