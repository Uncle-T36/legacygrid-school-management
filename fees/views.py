from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def fee_overview(request):
    """Fee overview"""
    return render(request, 'fees/fee_overview.html', {
        'title': 'Fee Management',
    })

@login_required
def fee_statements(request):
    """Fee statements"""
    return render(request, 'fees/fee_statements.html', {
        'title': 'Fee Statements',
    })

@login_required
def fee_categories(request):
    """Fee categories"""
    return render(request, 'fees/fee_categories.html', {
        'title': 'Fee Categories',
    })
