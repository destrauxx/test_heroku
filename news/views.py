from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from .forms import NewsModelForm, CommentaryModelForm
from .models import News, Commentaries, Likes



def read_view(request, *args, **kwargs):
    qs = News.objects.all()
    context = {'news_list': qs}
    return render(request, 'read.html', context)
def index(request, *args, **kwargs):
    return render(request, 'index.html')

def detail_view(request, pk):
    user = request.user
    liked = False
    try:
        obj = News.objects.get(id=pk)
    except News.DoesNotExist:
        raise Http404

    if request.user.is_authenticated and obj.likes.filter(user=user):
        liked = True
    return render(request, 'news/detail.html', {'single_object': obj, 'liked': liked})

@login_required
@permission_required('user.is_staff', raise_exception=True)
def create_view(request, *args, **kwargs):
    if request.method == 'POST':
        form = NewsModelForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.author = request.user
            obj.save()
            return render(request, 'forms.html', {"form": form, 'obj': obj})
    form = NewsModelForm(request.POST or None)
    return render(request, 'forms.html', {'form': form})


@login_required
@permission_required('user.is_staff')
def edit_view(request, pk):
    try:
        obj = News.objects.get(id=pk)
    except News.DoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = NewsModelForm(request.POST, instance = obj)
        if form.is_valid():
            edited_obj = form.save(commit=False)
            edited_obj.save()
    else:
        form = NewsModelForm(instance=obj)

    return render(request, 'edit_news_form.html', {'single_object' : obj, 'form': form})

@login_required
@permission_required('user.is_staff')
def delete_view(request, pk):
    try:
        obj = News.objects.get(id=pk)
    except News.DoesNotExist:
        raise Http404
    obj.delete()

    return HttpResponseRedirect(reverse('read'))

@login_required
def commentary_view(request, pk):
    form = CommentaryModelForm(request.POST or None)
    try:
        obj = News.objects.get(id=pk)
    except News.DoesNotExist:
        raise Http404

    if form.is_valid():
        text = form.cleaned_data.get('text')
        user = request.user
        commentary_obj = Commentaries(user=user, text=text)
        commentary_obj.save()
        obj.commentary.add(commentary_obj)
        obj.save()
        return HttpResponseRedirect(reverse('detail-news', args=[pk]))

    return render(request, 'news/commentary.html', {'single_object': obj, 'form': form})


@login_required
def likes_view(request, pk):
    try:
        obj = News.objects.get(id=pk)
    except News.DoesNotExist:
        raise Http404

    if request.method == "POST":
        user = request.user
        if not obj.likes.filter(user=user):
            like_obj = Likes(user=user, like=True)
            like_obj.save()
            obj.likes.add(like_obj)
            obj.save()
        else:
            obj.likes.filter(user=user).delete()

    return HttpResponseRedirect(reverse('detail-news', args=[pk]))

@login_required
def edit_commentary_view(request, pk, ck):
    try:
        obj = News.objects.get(id=pk)
        user = request.user
        commentary_obj = Commentaries.objects.get(id=ck)
    except News.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = CommentaryModelForm(request.POST or None, instance = commentary_obj)
        if form.is_valid():
            commentary_obj = form.save(commit=False)
            commentary_obj.save()
            return HttpResponseRedirect(reverse('detail-news', args=[pk]))
    else:
        form = CommentaryModelForm(instance=commentary_obj)

    return render(request, 'edit_commentary_form.html', {'single_object': obj, 'commentary': commentary_obj, 'form': form, 'user': user})

@login_required
def delete_commentary_view(request, pk, ck):
    try:
        obj = News.objects.get(id=pk)
        commentary_obj = Commentaries.objects.get(id=ck)
    except Commentaries.DoesNotExist:
        raise Http404
    obj.commentary.remove(commentary_obj)


    return HttpResponseRedirect(reverse('detail-news', args=[pk]))

