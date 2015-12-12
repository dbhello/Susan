#coding:utf8
from django.shortcuts import render, render_to_response
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import *
from django.shortcuts import get_object_or_404
from forms import *

borrowPeriod = datetime.timedelta(days=30)
reservedPeriod = datetime.timedelta(days=7)

def get_type_list():
	book_list = Book.objects.all()
	type_list = set()
	for book in book_list:
		type_list.add(book.typ)
	return list(type_list)


#delete the due reservations
def updateReservation():
	reservation = Reservation.objects.all()
	for res in reservation:
		if res.satisfyDate:
			if res.status == u"保留":
				if res.satisfyDate + reservedPeriod < datetime.date.today():
					res.status = u"过期未取"
					res.save()
		elif res.dueDate < datetime.date.today():
			res.status = u"已失效"
			res.save()


def index(req):
	username = req.session.get('username', '')
	if username:
		if len(username) == 8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	content = {'active_menu': 'homepage', 'user': user,'id_type':'home'}
	return render_to_response('homepage.html', content)

def signup(req):
	if req.session.get('username', ''):
		return HttpResponseRedirect('/')
	status = ''
	if req.POST:
		post = req.POST
		passwd = post.get('passwd', '')
		repasswd = post.get('repasswd', '')
		if passwd != repasswd:
			status = 're_err'
		else:
			username = post.get('username', '')
			if User.objects.filter(username=username):
				status = 'user_exist'
			else:
				newuser = User.objects.create_user(username=username, password=passwd, email=post.get('email', ''))
				newuser.save()
				new_myuser = Student(user=newuser, nickname=post.get('nickname'), permission=1)
				new_myuser.save()
				status = 'success'
				#login after signup
				user = auth.authenticate(username=username, password=passwd)
				auth.login(req, user)
				req.session['username'] = username
				return HttpResponseRedirect('/')
	content = {'active_menu': 'homepage', 'status': status, 'user': ''}
	return render_to_response('signup.html', content, context_instance=RequestContext(req))


def login(req):
	if req.session.get('username', ''):
		#update the reservation in database each time the user login
		updateReservation()
		return HttpResponseRedirect('/')
	status = ''
	if req.POST:
		post = req.POST
		username = post.get('username', '')
		password = post.get('passwd', '')
		user = auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(req, user)
				req.session['username'] = username
				return HttpResponseRedirect('/')
			else:
				status = 'not_active'
		else:
			status = 'not_exist_or_passwd_err'
	content = {'active_menu': 'login', 'status': status, 'user': ''}
	return render_to_response('login.html', content, context_instance=RequestContext(req))


def logout(req):
	auth.logout(req)
	return HttpResponseRedirect('/')


def setpasswd(req):
	username = req.session.get('username', '')
	if username != '':
		if len(username)==8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		return HttpResponseRedirect('/login/')
	status = ''
	if req.POST:
		post = req.POST
		if user.user.check_password(post.get('old', '')):
			if post.get('new', '') == post.get('new_re', ''):
				user.user.set_password(post.get('new', ''))
				user.user.save()
				status = 'success'
			else:
				status = 're_err'
		else:
			status = 'passwd_err'
	content = {'user': user, 'active_menu': 'setpasswd', 'status': status}
	return render_to_response('setpasswd.html', content, context_instance=RequestContext(req))


def addbook(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ""
		return HttpResponseRedirect('/login/')

	status = ""
	if req.method == 'POST':
		form = BookForm(req.POST or None, req.FILES)
		if form.is_valid():
			form.save()
			status = 'success'

	form = BookForm()
	return render(req, 'addbook.html', {'form': form,"user":user, 'status':status,'active_menu': 'homepage','id_type':'addbook'})


def viewbook(req):
	username = req.session.get('username', '')
	if username != '':
		if len(username)==8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	type_list = get_type_list()
	book_type = req.GET.get('typ', 'all')
	if book_type == '':
		book_lst = Book.objects.all()
	elif book_type not in type_list:
		book_type = 'all'
		book_lst = Book.objects.all()
	else:
		book_lst = Book.objects.filter(typ=book_type)

	if req.POST:
		post = req.POST
		keywords = post.get('keywords','')
		book_lst = Book.objects.filter(name__contains=keywords)
		book_type = 'all'

	paginator = Paginator(book_lst, 5)
	page = req.GET.get('page')
	try:
		book_list = paginator.page(page)
	except PageNotAnInteger:
		book_list = paginator.page(1)
	except EmptyPage:
		book_list = paginator.page(paginator.num_pages)

	content = {'user': user, 'active_menu': 'viewbook', 'type_list': type_list, 'book_type': book_type, 'book_list': book_list}
	return render_to_response('viewbook.html', content, context_instance=RequestContext(req))


def viewcopies(req):
	username = req.session.get('username', '')
	if username != '':
		if len(username)==8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	isbn = req.GET.get('isbn','')
	if isbn == '':
		return HttpResponseRedirect('/viewbook/')
	try:
		book = Book.objects.get(isbn=isbn)
	except:
		return HttpResponseRedirect('/viewbook/')

	bookcopies = BookCopy.objects.filter(book=book)
	duedate_lst = []
	request_lst = []
	status_lst = []

	for copy in bookcopies:
		borrows = BorrowInfo.objects.filter(bookcopy=copy)
		reservations = Reservation.objects.filter(bookcopy=copy,status__in=[u"处理中",u"保留"])
		request_lst.append(len(reservations))
		BORROW = False
		RESERVED = False
		for borrow in borrows:
			if not borrow.ReturnDate:
				BORROW = True
				duedate_lst.append(borrow.BorrowDate+borrowPeriod)
				if  user.permission == 2:
					status_lst.append('borrowed')
				else:
					if borrow.user.user.username == user.user.username:
						status_lst.append('my_borrow')
					else:
						for res in reservations:
							RESERVED = True
							if res.user.user.username == user.user.username:
								status_lst.append('my_reserved')
							else:
								status_lst.append('others_reserved')
						if not RESERVED:
							status_lst.append('others_borrow')
				break

		if not BORROW:
			duedate_lst.append("")
			if not reservations:
				status_lst.append('onboard')
			else:
				for res in reservations:
					if res.user.user.username == user.user.username:
						status_lst.append('my_reserved')
					else:
						status_lst.append('others_reserved')

	copy_due_req_status = zip(bookcopies,duedate_lst,request_lst,status_lst)
	content = {'user':user,'active_menu':'viewbook','book':book,'copy_due_req_status':copy_due_req_status}
	return render_to_response('viewcopies.html',content,context_instance=RequestContext(req))


def addreservation(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	selections = [u'东校区流通',u'北校区流通',u'南校区流通',u'珠海校区流通']
	id = req.GET.get('id','')
	if id == '':
		return HttpResponseRedirect('/viewbook/')
	try:
		bookcopy = BookCopy.objects.get(copy_id=id)
	except:
		return HttpResponseRedirect('/viewbook/')

	resDate = datetime.date.today()
	if bookcopy.status == "available":
		selections.remove(bookcopy.collection_loc)

	if req.POST:
		post = req.POST
		take_loc = post.get('take_loc','')
		dueDate = post.get('duedate','')
		reservation = Reservation(resDate=resDate,dueDate=dueDate,bookcopy=bookcopy,user=user,status=u'处理中',take_loc=take_loc)
		reservation.save()
		content =  {'user':user,'active_menu':'viewbook','bookcopy':bookcopy,'reservation':reservation}
		return render_to_response('addreservation_succeed.html',content,context_instance=RequestContext(req))

	content =  {'user':user,'active_menu':'viewbook','bookcopy':bookcopy,'resDate':resDate,'selections':selections}
	return render_to_response('addreservation.html',content,context_instance=RequestContext(req))


def frate(x):
	return {
		'excellent': 5,
		'good': 4,
		'average': 3,
		'fair': 2,
		'poor': 1,
	}.get(x, 5)


def detail(req):
	username = req.session.get('username','')
	if username != '':
		if len(username)==8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	isbn = req.GET.get('isbn','')
	if isbn == '':
		return HttpResponseRedirect('/viewbook/')
	try:
		book = Book.objects.get(isbn=isbn)
	except:
		return HttpResponseRedirect('/viewbook/')

	if req.POST:
		post = req.POST
		comment = post.get('comment','')
		now = datetime.date.today()
		eval = BookEval(book=book,user=user,evalDate=now,evalDesc=comment,rate='ex')
		eval.save()

	authors = [book.author]
	img_list = [book.img]
	book_eval = BookEval.objects.filter(book=book)
	rate_sum = 0
	rate_count = 0
	rate=0
	for eval in book_eval:
		rate_sum=rate_sum+frate(eval.rate)
		rate_count=rate_count+1
	if rate_count != 0:
		rate=rate_sum/rate_count
	rate_loop=['x']*rate
	rate_loop_empty=['x']*(5-rate)
	content = {'user': user, 'active_menu': 'viewbook','authors':authors, 'book': book,
			   'book_eval':book_eval,'img_list': img_list, 'rate_loop': rate_loop, 'rate_loop_empty': rate_loop_empty}
	return render_to_response('detail.html', content, context_instance=RequestContext(req))

def myaccount(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
        return HttpResponseRedirect('/index/')
    borrow_num = len(BorrowInfo.objects.filter(user=user,ReturnDate=None))
    borrowhistory_num = len(BorrowInfo.objects.filter(user=user))-borrow_num
    reservation_num = len(Reservation.objects.filter(user=user))
    content = {'user': user, 'active_menu': 'myaccount', 'borrow_num':borrow_num,
			   'borrowhistory_num':borrowhistory_num,'reservation_num':reservation_num}
    return render_to_response('myaccount.html', content)

def viewmember(req):
    username = req.session.get('username', '')
    if username != '':
        user = Librarian.objects.get(user__username=username)
    else:
        user = ''
        return HttpResponseRedirect('/login/')

    member_list = Librarian.objects.all()
    
    if req.POST:
        post = req.POST
        keywords = post.get('keywords','')
        member_list = Librarian.objects.filter(user__username__contains=keywords)
    content = {'user': user, 'active_menu': 'viewmember', 'member_list': member_list}
    return render_to_response('viewmember.html', content, context_instance=RequestContext(req))

def midifybaseinfo(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')
	status = ''
	if req.POST:
		post = req.POST
		user.name = post.get('name','')
		user.phone = post.get('phone','')
		user.address = post.get('address','')
		user.user.email = post.get('email','')
		user.major = post.get('major','')
		user.academy = post.get('academy','')
		user.politics = post.get('politics','')
		user.idcard = post.get('idcard','')
		user.education = post.get('education','')
		user.save()
		status = "success"
		return HttpResponseRedirect('/viewbaseinfo/')

	content = {'user':user,'active_menu':'homepage','status':status,'id_type':'viewbaseinfo'}
	return render_to_response("modifybaseinfo.html",content, context_instance=RequestContext(req))


def reservation(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	status = ""
	if req.GET:
		id = req.GET.get("id","")
		res = Reservation.objects.get(res_id=id)
		res.delete()
		status = "delete succeed"

	reservedDates = []
	reservation_info = Reservation.objects.filter(user=user)
	for res in reservation_info:
		if res.status == u"保留":
			reservedDates.append(res.satisfyDate+reservedPeriod)
		else:
			reservedDates.append("")
	reservations = zip(reservation_info,reservedDates)
	content = {'user':user,'active_menu':'homepage','id_type':'circulation','reservation_info':reservations,'status':status}
	return render_to_response("reservation.html",content, context_instance=RequestContext(req))


def borrow(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	borrow_info = BorrowInfo.objects.filter(user=user,ReturnDate=None)
	Due_list = []
	Fine = []
	for borrow in borrow_info:
		Due_list.append(borrow.BorrowDate + borrowPeriod)
		if (borrow.BorrowDate + borrowPeriod) < datetime.date.today():
			d = (datetime.date.today() - (borrow.BorrowDate + borrowPeriod)).days
			Fine.append(d*0.1)
			# user.permission = 0
			user.save()
		else:
			Fine.append(0)
	zipl = zip(borrow_info, Due_list, Fine)
	now = datetime.datetime.now()
	content = {'user': user, 'active_menu': 'homepage','id_type':'circulation','borrow_info': borrow_info, 'Due_list': Due_list, 'zipl': zipl, 'now': now}
	return render_to_response("borrow.html",content, context_instance=RequestContext(req))


def borrowhistory(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
        return HttpResponseRedirect('/login/')

    borrow_info = BorrowInfo.objects.filter(user=user)
    borrowhis = []
    Due_list = []
    Fine = []
    borrowPeriod = datetime.timedelta(days=30)
    for borrow in borrow_info:
        if borrow.ReturnDate:
            borrowhis.append(borrow)
            Due_list.append(borrow.BorrowDate + borrowPeriod)
            if borrow.BorrowDate + borrowPeriod < borrow.ReturnDate:
                d = (borrow.ReturnDate - (borrow.BorrowDate + borrowPeriod)).days
                Fine.append(d*0.1)
                user.permission = 0
                user.save()
            else:
                Fine.append(0)
    zipl = zip(borrowhis, Due_list, Fine)
    now = datetime.datetime.now()
    content = {'user': user, 'active_menu': 'homepage','id_type':'circulation', 'Due_list': Due_list, 'zipl': zipl, 'now': now}
    return render_to_response("borrowhistory.html",content, context_instance=RequestContext(req))


def borrowbook(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	borrowinfo =""
	status = ""
	dueDate = ""
	bookcopy = ""
	student = ""

	if req.POST:
		post = req.POST
		username = post.get('username',"")
		barcode = post.get('barcode','')
		if username and barcode:
			try:
				student = Student.objects.get(user__username=username)
				status = "has user"
			except:
				status = "no user"
			else:
				try:
					bookcopy = BookCopy.objects.get(barcode=barcode,collection_loc=user.loc) #location attention!!
				except:
					status = "no bookcopy"
				else:
					if bookcopy.status == 'borrowed':
						status = "borrowed"
						borrowinfo = BorrowInfo.objects.get(bookcopy=bookcopy,ReturnDate=None)
						dueDate = borrowinfo.BorrowDate + borrowPeriod
					else:
						try:
							reservation = Reservation.objects.get(bookcopy=bookcopy,status__in=[u"处理中",u"保留"])
							if reservation.user.user.username != username:
								status = "others_requested"
							elif reservation.user.user.username == username: #my requested, take the book
								status = "my_requested"
						except Reservation.DoesNotExist:
							status = "available"

		else:
			status = "information not complete"

	if req.GET:
		copy_id = req.GET.get('id',"")
		username = req.GET.get('username',"")
		bookcopy = BookCopy.objects.get(copy_id=copy_id)
		student = Student.objects.get(user__username=username)
		borrows = BorrowInfo.objects.all()
		if borrows:
			maxid = borrows[len(borrows)-1].borrow_id
		else:
			maxid = 0
		borrowinfo = BorrowInfo(user=student,bookcopy=bookcopy,BorrowDate=datetime.date.today(),borrow_id=maxid+1)
		borrowinfo.save()
		bookcopy.status = 'borrowed'
		bookcopy.save()
		book = Book.objects.get(isbn=bookcopy.book.isbn)
		book.borrowed_num += 1
		book.save()
		status = "borrow book succeed"
		dueDate = datetime.date.today()+borrowPeriod

		#if it is the requested reader to take the requested book
		try:
			reservation = Reservation.objects.get(bookcopy=bookcopy,user=student,status__in=[u"处理中",u"保留"])
			reservation.status = u"已取书"
			if not reservation.satisfyDate:
				reservation.satisfyDate = datetime.date.today()
			reservation.save()
		except Reservation.DoesNotExist:
			pass

	content = {'user': user, 'active_menu': 'homepage','bookcopy':bookcopy,'borrowinfo':borrowinfo,\
			   'due':dueDate,'status':status,\
			   'id_type':'borrowbook','student':student}
	return render_to_response("borrowbook.html",content, context_instance=RequestContext(req))


def returnbook(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	status = ""
	REQUEST = False
	borrow_info = ""
	bookcopy = ""
	fine = 0
	dueDate = ""

	if req.POST:
		post = req.POST
		barcode = post.get('barcode','')
		if barcode:
			try:
				bookcopy = BookCopy.objects.get(barcode=barcode)
			except BookCopy.DoesNotExist:
				status = "no bookcopy"
			else:
				try:
					borrow_info = BorrowInfo.objects.get(bookcopy=bookcopy,ReturnDate=None)
				except BorrowInfo.DoesNotExist:
					status = "available"
				else:
					status = "borrowed"
					dueDate = borrow_info.BorrowDate + borrowPeriod
					if dueDate < datetime.date.today():
						d = (datetime.date.today() - dueDate).days
						fine = d*0.1
					try:
						reservation = Reservation.objects.get(bookcopy=bookcopy,status=u"处理中")
						REQUEST = True
					except Reservation.DoesNotExist:
						REQUEST = False

		else:
			status = "information not complete"

	if req.GET:
		id = req.GET.get('id','')
		if id:
			try:
				bookcopy = BookCopy.objects.get(copy_id=id)
				book = Book.objects.get(isbn=bookcopy.book.isbn)
				borrow_info = BorrowInfo.objects.get(bookcopy=bookcopy,ReturnDate=None)
				borrow_info.ReturnDate = datetime.date.today()
				borrow_info.save()
				bookcopy.status = 'available'
				# bookcopy.collection_loc = user.loc  #attention, revise the locations
				bookcopy.save()
				book.borrowed_num -= 1
				book.save()
				status = "return book succeed"

				#if someone reserved this book
				try:
					reservation = Reservation.objects.get(bookcopy=bookcopy,status=u"处理中")
					REQUEST = True
					if reservation.take_loc == user.loc:
						reservation.status = u"保留"
						reservation.satisfyDate = datetime.date.today()
						reservation.save()
						####send a reservation satisfied email

				except Reservation.DoesNotExist:
					REQUEST = False

				dueDate = borrow_info.BorrowDate + borrowPeriod
				if dueDate < datetime.date.today():
					d = (datetime.date.today() - dueDate).days
					fine = d*0.1
				else:
					fine = 0
			except Exception as e:
				print e
				return HttpResponseRedirect('/returnbook/')

	content = {'user': user, 'active_menu': 'homepage','bi':borrow_info,'bookcopy':bookcopy,'due':dueDate,
			   'fine':fine,'status':status,'id_type':'returnbook','request':REQUEST}
	return render_to_response("returnbook.html",content, context_instance=RequestContext(req))


def processreservation(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	part_res = []
	reservation = Reservation.objects.filter(status=u"处理中")
	for res in reservation:
		if res.bookcopy.collection_loc == user.loc and res.bookcopy.status == "available":  #find the requested bookcopy in this collection loc
			part_res.append(res)

	paginator = Paginator(part_res, 10)
	page = req.GET.get('page')
	try:
		res_list = paginator.page(page)
	except PageNotAnInteger:
		res_list = paginator.page(1)
	except EmptyPage:
		res_list = paginator.page(paginator.num_pages)

	content = {'user': user, 'active_menu': 'homepage','id_type':'processreservation','res_list':res_list}
	return render_to_response("processreservation.html",content, context_instance=RequestContext(req))


def notification(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	status = ""
	if req.method == 'POST':
		form = notificaitonForm(req.POST or None, req.FILES)
		if form.is_valid():
			form.save()
			status = 'success'

	form = notificaitonForm()
	return render(req, 'notification.html', {'form': form,"user":user, 'status':status,'active_menu': 'homepage','id_type':'notification'})


def adduser(req):
	username = req.session.get('username', '')
	if username != '':
		user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')
	content = {'user': user, 'active_menu': 'homepage'}
	return render_to_response("adduser.html",content, context_instance=RequestContext(req))

def homepage(req):
	username = req.session.get('username', '')
	if username != '':
		if len(username)==8:
			user = Student.objects.get(user__username=username)
		else:
			user = Librarian.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')
	content = {'user': user, 'active_menu': 'homepage','id_type':'home'}
	return render_to_response("homepage.html",content, context_instance=RequestContext(req))


def viewnotification(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	if req.GET:
		id = req.GET.get("id","")
		notice = Notification.objects.get(id=id)
		content = {'user': user, 'active_menu': 'homepage','id_type':'viewnotification','notice':notice}
		return render_to_response("noticedetail.html",content, context_instance=RequestContext(req))

	notification = Notification.objects.all()
	content = {'user': user, 'active_menu': 'homepage','id_type':'viewnotification','notificaiton':notification,'num':len(notification)}
	return render_to_response("viewnotification.html",content, context_instance=RequestContext(req))

def viewbaseinfo(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	content = {'user': user, 'active_menu': 'homepage','id_type':'viewbaseinfo'}
	return render_to_response("viewbaseinfo.html",content, context_instance=RequestContext(req))

def circulation(req):
	username = req.session.get('username', '')
	if username != '':
		user = Student.objects.get(user__username=username)
	else:
		user = ''
		return HttpResponseRedirect('/login/')

	borrow_num = len(BorrowInfo.objects.filter(user=user,ReturnDate=None))
	borrowhistory_num = len(BorrowInfo.objects.filter(user=user))-borrow_num
	reservation_num = len(Reservation.objects.filter(user=user))

	content = {'user': user, 'active_menu': 'homepage','id_type':'circulation',
			   'borrow_num':borrow_num,'borrowhistory_num':borrowhistory_num, 'reservation_num':reservation_num}
	return render_to_response("circulation.html",content, context_instance=RequestContext(req))