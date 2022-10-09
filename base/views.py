from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm

# Create your views here.


def loginPage(request):
    page = 'login'
    # 이미 로그인한 유저 재로그인 방지
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # 존재하는 유저인지 확인
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, '존재하지 않는 유저명입니다.')

        # 유저가 존재하면 맞는지 확인하기
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '잘못된 유저명, 혹은 비밀번호입니다.')
    context = {
        'page': page
    }
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # 데이터 전처리
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '회원 가입 도중 오류가 발생했습니다. 다시 시도해주세요.')

    return render(request, 'base/login_register.html', {'form': form})



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

    # 현재 보고 있는 방의 메세지만 피드에 출력
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )


    context = {
        'rooms' : rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()


    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
            )
        room.participants.add(request.user)
        # 포스트 방식이므로 새로고침 한번 해주기
        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants,
    }        
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.room_set.all()   
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {
        'user': user, 
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics,
    }
    return render(request, 'base/profile.html', context)



# 로그인이 되어있지 않으면 로그인 url로 보내기
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()

    if request.method == 'POST':
        # 터미널에서 출력하기
        # print(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),

        )
        return redirect('home')
    context = {
        'form' : form,
        'topics': topics,
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(pk=pk)
    # 업데이트할 룸을 지정해주기
    form = RoomForm(instance=room)
    topics = Topic.objects.all()


    # 유저 확인해주기
    if request.user != room.host:
        return HttpResponse('자신이 개설한 방만 편집할 수 있습니다.')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {
        'room': room,
        'form' : form,
        'topics': topics
    }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(pk=pk)
    
    # 유저 확인해주기
    if request.user != room.host:
        return HttpResponse('자신이 개설한 방만 편집할 수 있습니다.')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', { 'obj' : room })


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(pk=pk)
    
    # 유저 확인해주기
    if request.user != message.user:
        return HttpResponse('자신이 작성한 글만 삭제할 수 있습니다.')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', { 'obj' : message }) 

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.pk)

    return render(request, 'base/update-user.html', {'form': form})