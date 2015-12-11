from django.contrib import admin
from management.models import *

class BookAdmin(admin.ModelAdmin):
	list_display = ('isbn', 'name', 'typ', 'pubDate', 'call_number', 'desc','copies_num','borrowed_num','img')

class BookCopyAdmin(admin.ModelAdmin):
	list_display = ('copy_id','barcode','status','collection_loc')
	ordering = ('barcode',)

class AuthorAdmin(admin.ModelAdmin):
	list_display = ('name','email')
	ordering = ('name',)

class PublisherAdmin(admin.ModelAdmin):
	list_display = ('publisher_id','name','address','website')
	ordering = ('publisher_id',)

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('time','content','librarian')
	ordering = ('time',)

class ReservationAdmin(admin.ModelAdmin):
	list_display = ('res_id','user','resDate','dueDate','status','satisfyDate','take_loc')
	search_fields = ('user',)
	ordering = ('res_id',)

class BorrowInfoAdmin(admin.ModelAdmin):
	list_display = ('borrow_id','bookcopy','user','BorrowDate','ReturnDate')
	search_fields = ('user',)
	ordering = ('bookcopy',)

class StudentAdmin(admin.ModelAdmin):
	list_display = ("user","name","phone","address","major","academy","education","politics")
	ordering = ("user",)
	search_fields = ("user",)

class LibrarianAdmin(admin.ModelAdmin):
	list_display = ("user","name","phone","address")
	ordering = ("user",)
	search_fields = ("user",)

admin.site.register(Student,StudentAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(Book,BookAdmin)
admin.site.register(Publisher,PublisherAdmin)
admin.site.register(Author,AuthorAdmin)
admin.site.register(BookCopy,BookCopyAdmin)
admin.site.register(Reservation,ReservationAdmin)
admin.site.register(BorrowInfo,BorrowInfoAdmin)
admin.site.register(BookEval)
admin.site.register(Message)
admin.site.register(Librarian,LibrarianAdmin)
