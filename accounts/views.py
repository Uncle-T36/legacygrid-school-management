from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import User, AuditLog, LoginHistory
from .forms import CustomUserCreationForm, UserProfileForm, LoginForm
from .decorators import role_required, audit_action


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@audit_action('login_attempt')
def custom_login(request):
    """Custom login view with security features"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            try:
                user = User.objects.get(username=username)
                
                # Check if account is locked
                if user.is_account_locked():
                    messages.error(request, 'Account is temporarily locked due to multiple failed attempts.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Authenticate user
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    user.reset_failed_attempts()
                    user.last_activity = timezone.now()
                    user.is_active_session = True
                    user.save()
                    
                    # Log successful login
                    LoginHistory.objects.create(
                        user=user,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=True
                    )
                    
                    messages.success(request, f'Welcome back, {user.get_full_name()}!')
                    return redirect('dashboard')
                else:
                    # Handle failed login
                    try:
                        user = User.objects.get(username=username)
                        user.increment_failed_attempts()
                        
                        # Log failed login
                        LoginHistory.objects.create(
                            user=user,
                            ip_address=get_client_ip(request),
                            user_agent=request.META.get('HTTP_USER_AGENT', ''),
                            success=False,
                            failure_reason='Invalid credentials'
                        )
                    except User.DoesNotExist:
                        pass
                    
                    messages.error(request, 'Invalid username or password.')
                    
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@audit_action('logout')
def custom_logout(request):
    """Custom logout view"""
    if request.user.is_authenticated:
        # Update login history
        try:
            last_login = LoginHistory.objects.filter(
                user=request.user, 
                logout_time__isnull=True
            ).first()
            if last_login:
                last_login.logout_time = timezone.now()
                last_login.save()
        except:
            pass
        
        # Update user session status
        request.user.is_active_session = False
        request.user.save()
        
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    
    return redirect('home')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@audit_action('profile_view')
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
@audit_action('profile_update')
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def dashboard(request):
    """Main dashboard view with role-based content"""
    context = {
        'user': request.user,
        'role': request.user.role,
    }
    
    # Add role-specific context
    if request.user.role == 'owner' or request.user.is_superuser:
        # Owner dashboard data
        context.update({
            'total_students': User.objects.filter(role='student').count(),
            'total_teachers': User.objects.filter(role='teacher').count(),
            'total_parents': User.objects.filter(role='parent').count(),
            'recent_activities': AuditLog.objects.select_related('user')[:10],
        })
    elif request.user.role == 'admin':
        # Admin dashboard data
        context.update({
            'students_count': User.objects.filter(role='student', school=request.user.school).count(),
            'teachers_count': User.objects.filter(role='teacher', school=request.user.school).count(),
        })
    elif request.user.role == 'teacher':
        # Teacher dashboard data
        pass  # Will be implemented in students app
    elif request.user.role == 'parent':
        # Parent dashboard data
        pass  # Will be implemented in students app
    elif request.user.role == 'student':
        # Student dashboard data
        pass  # Will be implemented in students app
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
@role_required(['owner', 'admin'])
@audit_action('user_management')
def user_management(request):
    """User management for admins and owners"""
    users = User.objects.all().order_by('role', 'last_name', 'first_name')
    
    # Filter by school for non-owners
    if request.user.role != 'owner' and not request.user.is_superuser:
        users = users.filter(school=request.user.school)
    
    context = {
        'users': users,
        'roles': User.ROLE_CHOICES,
    }
    
    return render(request, 'accounts/user_management.html', context)


@login_required
@role_required(['owner'])
@audit_action('audit_log_view')
def audit_log(request):
    """View audit logs - owner only"""
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    
    return render(request, 'accounts/audit_log.html', {'logs': logs})
