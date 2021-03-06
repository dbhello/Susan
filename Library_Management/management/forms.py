#coding=utf8
from django import forms
from models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("name","phone","address")

class notificaitonForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('title','time','content','pub_person')

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('isbn','name','call_number','typ','pubDate','publisher','author','copies_num','desc','img')