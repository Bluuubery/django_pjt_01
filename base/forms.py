from django.forms import ModelForm
from .models import Room

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']
        
        # fields = ['name', 'contents',] 와 같이 특정 요소만을 불러올 수 잇음