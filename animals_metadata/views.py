# views.py
from django.shortcuts import render

from .models import ViralInjection


def viral_injection_list_view(request):
    # Fetch all viral injections along with their related animal data
    injections = ViralInjection.objects.select_related('animal').all()
    
    # Pass the injections list to the HTML template
    context = {'injections': injections}
    return render(request, 'viral_injections.html', context)