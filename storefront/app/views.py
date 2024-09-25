from django.shortcuts import render
from .models import Tweet
from .forms import TweetForm, UserRegistrationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.http import JsonResponse
# Create your views here.

def index(request):
    return render(request, 'index.html')

def tweet_list(request):
    query = request.GET.get('q')  # Get the search query from the URL parameters
    
    if query:
        tweets = Tweet.objects.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
        ).order_by('-created_at')  # Filter tweets based on text or username
    else:
        tweets = Tweet.objects.all().order_by('-created_at')  # Show all tweets if no query
    
    return render(request, 'tweet_list.html', {'tweets': tweets, 'query': query})


@login_required
def tweet_create(request):
    if request.method == "POST":
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm()
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_edit(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user = request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})

@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    
    if request.method == 'POST':
        tweet.delete()
        
        # Check if the request is an AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'}, status=200)
        else:
            # Fallback for non-AJAX requests, like in your original code
            return redirect('tweet_list')
    
    # If it's a GET request, you can choose to render a confirmation page
    return render(request, 'tweet_delete.html', {'tweet': tweet})      

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # UserCreationForm already hashes the password
            login(request, user)  # Log the user in after registration
            return redirect('tweet_list') # Use reverse for more clarity
    else:
        form = UserRegistrationForm()       
    return render(request, 'registration/register.html', {'form': form})


         

