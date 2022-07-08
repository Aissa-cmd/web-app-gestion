from django.shortcuts import render
from django.contrib.auth.decorators import permission_required

@permission_required('main.view_help')
def help_index(request):
    return render(request, 'help/index.html')

@permission_required('main.view_help')
def help_dashboard(request):
    return render(request, 'help/dashboard/index.html')

@permission_required('main.view_help')
def help_domains(request):
    return render(request, 'help/domains/index.html')

@permission_required('main.view_help')
def help_groups(request):
    return render(request, 'help/groups/index.html')

@permission_required('main.view_help')
def help_orders(request):
    return render(request, 'help/orders/index.html')

@permission_required('main.view_help')
def help_products(request):
    return render(request, 'help/products/index.html')

@permission_required('main.view_help')
def help_users(request):
    return render(request, 'help/users/index.html')
