from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout  # Import logout function
from .models import Members  # Import your custom Members model
from django.contrib.auth.hashers import check_password 
from django.contrib.auth.hashers import make_password
from django import forms
from .models import Tasks
from .forms import TaskForm
from django.utils.timezone import now

from .forms import SubscriptionForm
from .models import Subscription

def home(request):
    return render(request, 'home.html', {})

def signup(request):
    if request.method == "POST":
        # Get data from the form
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check if password and confirm_password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('signup')

        # Check if email already exists in the Members table
        if Members.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect('signup')

        # Hash the password before saving it
        hashed_password = make_password(password)

        # Save the new user in the Members table with hashed password
        new_member = Members(username=username, email=email, password=hashed_password)
        new_member.save()

        messages.success(request, "Your account has been successfully created.")
        return redirect('signin')  # Redirect to the sign-in page

    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        # Get data from the form
        email = request.POST['email']
        password = request.POST['password']

        try:
            # Check if the email exists in the Members table
            member = Members.objects.get(email=email)

            # Verify the password (if hashed in the Members table)
            if check_password(password, member.password):
                # Password matches, assign session variables
                request.session['member_id'] = member.id
                request.session['member_username'] = member.username

                # Redirect to the task page (or user dashboard)
                messages.success(request, "Successfully logged in!")
                return redirect('taskpage')
            else:
                messages.error(request, "Incorrect password!")
        except Members.DoesNotExist:
            messages.error(request, "No account found with that email!")

    return render(request, "signin.html")

# Define the taskpage view
def taskpage(request):
    if not request.session.get('member_id'):
        return redirect('signin')  # Redirect unauthenticated users

    # Fetch the logged-in user's ID
    member_id = request.session.get('member_id')

    # Fetch tasks owned by the logged-in user
    tasks = Tasks.objects.filter(owner_id=member_id, deleted=False)
    tasks_deleted = Tasks.objects.filter(owner_id=member_id, deleted=True)

    # Optional filters
    status_filter = request.GET.get('status')  # Get the status filter value
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    # Date range filter (optional)
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from and date_to:
        tasks = tasks.filter(due_date__range=[date_from, date_to])

    # Pass the status_filter to the template
    context = {
        'tasks': tasks,
        'tasks_deleted': tasks_deleted,
        'status_filter': status_filter,  # Include the selected status filter
    }
    return render(request, 'taskpage.html', context)


def add_task(request):
    if not request.session.get('member_id'):
        return redirect('signin')

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            member_id = request.session.get('member_id')
            owner = Members.objects.get(id=member_id)
            task = form.save(commit=False)
            task.owner = owner
            task.save()
            messages.success(request, "Task added successfully!")
            return redirect('taskpage')
    else:
        form = TaskForm()

    return render(request, 'add_task.html', {'form': form})
    
def edit_task(request, task_id):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('signin')

    task = Tasks.objects.get(id=task_id, owner_id=member_id)
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated successfully!")
            return redirect('taskpage')
    else:
        form = TaskForm(instance=task)

    return render(request, 'edit_task.html', {'form': form, 'task': task})


def delete_task(request, task_id):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('signin')

    try:
        task = Tasks.objects.get(id=task_id, owner_id=member_id, deleted=False)  # Ensure task isn't already deleted
        task.deleted = True
        task.deleted_at = now()
        task.save()
        messages.success(request, "Task has been deleted.")
    except Tasks.DoesNotExist:
        messages.error(request, "Task not found or already deleted.")
    
    return redirect('taskpage')

def batch_delete_tasks(request):
    if request.method == "POST":
        member_id = request.session.get('member_id')
        if not member_id:
            return redirect('signin')

        date_from = request.POST['date_from']
        date_to = request.POST['date_to']
        Tasks.objects.filter(owner_id=member_id, due_date__range=[date_from, date_to]).delete()
        return redirect('taskpage')
    
def restore_task(request, task_id):
    member_id = request.session.get('member_id')
    if not member_id:
        return redirect('signin')

    try:
        task = Tasks.objects.get(id=task_id, owner_id=member_id, deleted=True)  # Fetch deleted task
        task.deleted = False
        task.deleted_at = None
        task.save()
        messages.success(request, "Task has been restored.")
    except Tasks.DoesNotExist:
        messages.error(request, "Task not found or already restored.")
    
    return redirect('taskpage')

def logout_user(request):
    try:
        del request.session['member_id']
        del request.session['member_username']
    except KeyError:
        pass  # If no user is logged in, continue without errors
    
    messages.success(request, "You have been logged out successfully.")
    return redirect('signin')

################################################

def subscribe(request):
    if not request.session.get('member_id'):
        return redirect('signin')

    member_id = request.session.get('member_id')
    user = Members.objects.get(id=member_id)

    if request.method == "POST":
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            subscription, created = Subscription.objects.update_or_create(
                user=user,
                defaults=form.cleaned_data
            )
            messages.success(request, "Subscription updated successfully!" if not created else "Subscription created!")
            return redirect('taskpage')
    else:
        try:
            subscription = user.subscription
            form = SubscriptionForm(instance=subscription)
        except Subscription.DoesNotExist:
            form = SubscriptionForm()

    return render(request, 'subscribe.html', {'form': form})

def unsubscribe(request):
    if not request.session.get('member_id'):
        return redirect('signin')

    member_id = request.session.get('member_id')
    user = Members.objects.get(id=member_id)

    try:
        user.subscription.delete()
        messages.success(request, "Subscription cancelled.")
    except Subscription.DoesNotExist:
        messages.error(request, "No subscription found.")

    return redirect('taskpage')