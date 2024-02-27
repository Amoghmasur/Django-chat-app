from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Thread,User,Group
from itertools import chain
from django.db.models import Value, BooleanField
from django.forms.models import model_to_dict





@login_required
def messages_page(request):
    threads = Thread.objects.by_user(user=request.user).prefetch_related('chatmessage_thread').order_by('timestamp')
    groups = Group.objects.filter(members=request.user).prefetch_related('groupmessage_group').order_by('created_at')

    threads = threads.annotate(is_thread=Value(True, output_field=BooleanField()))
    groups = groups.annotate(is_group=Value(True, output_field=BooleanField()))

# Combining threads and groups

    threads_and_groups = list(chain(threads, groups))

    context = {
        'threads': threads,
        'groups':groups,
        'threads_and_groups':threads_and_groups,
    }
    return render(request, 'messages.html',context)





@login_required
def search_users(request):
    query = request.GET.get('query', '')
    users = User.objects.filter(username__icontains=query).exclude(id=request.user.id).values('id', 'username')
    return JsonResponse(list(users), safe=False)



@login_required
def create_thread(request):
    selected_user_id = request.POST.get('selected_user_id')
    selected_user = User.objects.get(id=selected_user_id)
    thread, created = Thread.objects.get_or_create(
        first_person=request.user,
        second_person=selected_user
    )
    chat_url = '/chat/'
    return JsonResponse({'unique_id': str(thread.unique_id), 'created': created, 'redirect_url': chat_url})





# In your views.py

@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        if group_name:
            # Create the group and add the user
            group = Group.objects.create(name=group_name)
            group.members.add(request.user)
            chat_url = '/chat/'
            return JsonResponse({'group_unique_id': group.unique_id,'redirect_url': chat_url})
        else:
            return JsonResponse({'error': 'Invalid group name'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)




@login_required
def search_users_add_to_group(request, group_unique_id):
    query = request.GET.get('query', '')
    group = Group.objects.get(unique_id=group_unique_id)

    # group_data = model_to_dict(group, fields=['id', 'name', 'unique_id'])

    users = User.objects.filter(username__icontains=query).exclude(id__in=group.members.all()).values('id', 'username')
    return JsonResponse(list(users) ,safe=False)
 

@login_required
def add_to_group(request):
    selected_user_id = request.POST.get('selected_user_id')
    selected_group_unique_id = request.POST.get('selected_group_unique_id')

    group = Group.objects.get(unique_id=selected_group_unique_id)
    user = User.objects.get(id=selected_user_id)

    group.members.add(user)

    chat_url = '/chat/'
    return JsonResponse({'redirect_url': chat_url})
