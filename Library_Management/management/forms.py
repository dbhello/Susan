#coding=utf8
from django import forms
from models import *

class UserForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ("name","phone")


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ('isbn','name','call_number','typ','desc','img')


