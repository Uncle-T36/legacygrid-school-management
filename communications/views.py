from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def messages_inbox(request):
    """Messages inbox"""
    return render(request, 'communications/messages_inbox.html', {
        'title': 'Messages',
    })

@login_required
def compose_message(request):
    """Compose new message"""
    return render(request, 'communications/compose_message.html', {
        'title': 'Compose Message',
    })

@login_required
def notification_list(request):
    """List notifications"""
    return render(request, 'communications/notification_list.html', {
        'title': 'Notifications',
    })
