from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm

# Create your views here.



def home(request):
    q= request.GET.get('q') if request.GET.get('q') != None else ''

    # icontains: 포함하도록 나중에 찾아보자,,,
    # Q 동적 쿼리 메소드 ... 나중에 찾아보자,,,
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    # 나중에 필터로 상위 n개만 걸러내는 기능 추가하기
    topics = Topic.objects.all()
    # len도 가능한데 len보다 이게 나음
    room_count = rooms.count()

    context = {
        'rooms' : rooms,
        'topics': topics,
        'room_count': room_count,
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(pk=pk)
    context = {
        'room': room,
    }        
    return render(request, 'base/room.html', context)


def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        # 터미널에서 출력하기
        # print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {
        'form' : form
    }
    return render(request, 'base/room_form.html', context)


def updateRoom(request, pk):
    room = Room.objects.get(pk=pk)
    # 업데이트할 룸을 지정해주기
    form = RoomForm(instance=room)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {
        'form' : form
    }
    return render(request, 'base/room_form.html', context)


def deleteRoom(request, pk):
    room = Room.objects.get(pk=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', { 'obj' : room })