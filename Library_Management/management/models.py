#coding:utf8
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from choice import *

class Student(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(u"姓名",max_length = 16)
    phone = models.CharField(u"电话",max_length = 11)
    address = models.CharField(u"地址",max_length = 300)
    major = models.CharField(u"专业",max_length=50)
    education = models.CharField(u"学历",max_length=30)
    politics = models.CharField(u"政治面貌",max_length = 30)
    academy = models.CharField(u"学院",max_length = 50)
    idcard = models.CharField(u"身份证号",max_length=18)
    def __unicode__(self):
        return self.name

class Librarian(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField(u"姓名",max_length = 16)
    phone = models.CharField(u"电话",max_length = 11)
    address = models.CharField(u"地址",max_length = 300)
    def __unicode__(self):
        return self.name

class Publisher(models.Model):
    publisher_id = models.IntegerField(u"出版社编号",primary_key=True)
    name = models.CharField(u"出版社",max_length=30)
    address = models.CharField(u"地址",max_length=50)
    website = models.URLField(u"网站")
    def __unicode__(self):
        return self.name

class Author(models.Model):
    author_id = models.IntegerField(u"作者编号",primary_key=True)
    name = models.CharField(u"作者姓名",max_length=100)
    email = models.EmailField(u"邮箱")
    def __unicode__(self):
        return self.name

class Book(models.Model):
    isbn = models.CharField(max_length = 200,primary_key = True)
    call_number = models.CharField(u"索引号",max_length=200)
    name = models.CharField(u"书名",max_length = 128)
    pubDate = models.DateField(u"出版日期")
    typ = models.CharField(u"图书类型",max_length = 128)
    desc = models.CharField(u"详情",max_length=1000)
    copies_num = models.IntegerField(u"复本数目")
    borrowed_num = models.IntegerField(u"已借复本数目")
    img = models.ImageField(u"封面",upload_to = 'image')
    author = models.ForeignKey(Author)
    publisher = models.ForeignKey(Publisher)

    class META:
        ordering = ['name']

    def __unicode__(self):
        return self.name

class BookCopy(models.Model):
    book = models.ForeignKey(Book)
    copy_id = models.IntegerField(u"单册编号",primary_key=True)
    barcode = models.CharField(u"条形码",max_length=30)
    status = models.CharField(u"单册状态",max_length=10,choices=BOOK_STATUS,default='外借本')
    collection_loc = models.CharField(u"馆藏地点",max_length=10,choices=LOC_CHOICE,default='东校区流通')
    class META:
        ordering = ['copy_id']
    def __unicode__(self):
        # return u'%s %s' % (self.copy_id,self.book.name)
        return self.barcode

class Notification(models.Model):
    librarian = models.ForeignKey(Librarian)
    title = models.CharField(u"通知标题",max_length=50)
    time = models.DateTimeField(u"通知时间")
    content = models.TextField(u"通知内容")
    class META:
        ordering = ['time']

    def __unicode__(self):
        return self.title

class Message(models.Model):
    student = models.ForeignKey(Student)
    msg_title = models.CharField(u"消息标题",max_length=50)
    msg_content = models.TextField(u"消息内容")
    msg_time = models.DateTimeField(u"消息时间")
    class META:
        ordering = ['msg_time']
    def __unicode__(self):
        return self.msg_title

class Reservation(models.Model):
    res_id = models.IntegerField(u"预约编号",primary_key=True)
    bookcopy = models.ForeignKey(BookCopy)
    user = models.ForeignKey(Student)
    resDate = models.DateField(u"预约日期")
    dueDate = models.DateField(u"过期日期")
    satisfyDate = models.DateField(u"满足日期",blank=True,null=True)
    status = models.CharField(u"请求状态",max_length=40,choices=RESERVE_STATUS,default=u"处理中")
    take_loc = models.CharField(u"取书地点",max_length=30,choices=LOC_CHOICE,default=U'东校区流通')

    def __unicode__(self):
        return u"%s %s" % (self.bookcopy.book.name, self.user.name)

class BorrowInfo(models.Model):
    borrow_id = models.IntegerField(u"借书编号",primary_key=True)
    bookcopy=models.ForeignKey(BookCopy)
    user=models.ForeignKey(Student)
    BorrowDate = models.DateField(u"借书日期")
    ReturnDate = models.DateField(u"还书日期",null=True,blank=True)

    def __unicode__(self):
        return u"%s %s" % (self.bookcopy.book.name, self.user.name)

class BookEval(models.Model):
    eval_id = models.IntegerField(u"评价编号",primary_key=True)
    book=models.ForeignKey(Book)
    user=models.ForeignKey(Student)
    rate = models.CharField(u"评价等级",max_length=2,choices=RATE_CHOICE,default='excellent')
    evalDesc = models.CharField(u"评价内容",max_length=500)
    evalDate = models.DateField(u"评价时间")

    def __unicode__(self):
        return self.book.name





