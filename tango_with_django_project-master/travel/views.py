from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


def home(request):
    return HttpResponse("<h1>Scotland Travel App is running ✅</h1>")

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