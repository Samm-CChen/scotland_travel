from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from .models import Attraction, Bookmark

def home(request):
    return render(request, "travel/home.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("travel:home")

    next_url = request.GET.get("next") or request.POST.get("next") or settings.LOGIN_REDIRECT_URL

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account has been created.")

            if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect(settings.LOGIN_REDIRECT_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form, "next": next_url})

def cities(request):
    return HttpResponse("Cities page")
    
def attraction_detail(request, attraction_id):
    attraction = get_object_or_404(Attraction, pk=attraction_id)
    is_bookmarked = False

    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, attraction=attraction).exists()

    return render(request, "travel/attraction_detail.html", {
        "attraction": attraction,
        "is_bookmarked": is_bookmarked,
    })

@login_required
def toggle_bookmark(request, attraction_id):
    if request.method != "POST":
        return redirect("travel:attraction_detail", attraction_id=attraction_id)

    attraction = get_object_or_404(Attraction, pk=attraction_id)

    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        attraction=attraction
    )

    if not created:
        bookmark.delete()

    return redirect("travel:attraction_detail", attraction_id=attraction_id)

@login_required
def bookmarks(request):
    qs = (Bookmark.objects
          .filter(user=request.user)
          .select_related("attraction", "attraction__city")
          .order_by("-created_at"))

    return render(request, "travel/bookmarks.html", {"bookmarks": qs})

@login_required
def protected(request):
    return HttpResponse("You are logged in ✅")