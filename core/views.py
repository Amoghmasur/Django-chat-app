from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import auth

from .forms import SignUpForm

def frontpage(request):
    return render(request, 'core/frontpage.html')




def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = SignUpForm()

    context = {
        'form': form,
    }
    
    return render(request, 'core/signup.html', context)



def logout(request):
    auth.logout(request)
    return redirect('/')