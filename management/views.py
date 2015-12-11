# coding:utf8
from django.shortcuts import render, render_to_response
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import datetime
from django import forms
from django.contrib.auth.models import User
from django.contrib import auth
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from models import *

borrowPeriod = datetime.timedelta(days=30)


def get_type_list():
    book_list = Book.objects.all()
    type_list = set()
    for book in book_list:
        type_list.add(book.typ)
    return list(type_list)


def index(req):
    username = req.session.get('username', '')
    if username:
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    content = {'active_menu': 'homepage', 'user': user}
    return render_to_response('index.html', content)


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
                # login after signup
                user = auth.authenticate(username=username, password=passwd)
                auth.login(req, user)
                req.session['username'] = username
                return HttpResponseRedirect('/')
    content = {'active_menu': 'homepage', 'status': status, 'user': ''}
    return render_to_response('signup.html', content, context_instance=RequestContext(req))


def login(req):
    if req.session.get('username', ''):
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
    content = {'active_menu': 'homepage', 'status': status, 'user': ''}
    return render_to_response('login.html', content, context_instance=RequestContext(req))


def logout(req):
    auth.logout(req)
    return HttpResponseRedirect('/')


def setpasswd(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
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
    content = {'user': user, 'active_menu': 'homepage', 'status': status}
    return render_to_response('setpasswd.html', content, context_instance=RequestContext(req))


def addbook(req):
    username = req.session.get('username', '')
    if username != '':
        user = Librarian.objects.get(user__username=username)
    else:
        return HttpResponseRedirect('/login/')
    if user.permission < 2:
        return HttpResponseRedirect('/')
    status = ''
    if req.POST:
        post = req.POST
        newbook = Book(
            name=post.get('name', ''),
            isbn=post.get('isbn', ''),
            publisher=post.get('publisher', ''),
            author=post.get('author', ''),
            typ=post.get('typ', ''),
            price=post.get('price', ''),
            pubDate=post.get('pubdate', ''),
            )
        newbook.save()
        status = 'success'
    content = {'user': user, 'active_menu': 'addbook', 'status': status}
    return render_to_response('addbook.html', content, context_instance=RequestContext(req))


def viewbook(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
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
        keywords = post.get('keywords', '')
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

    content = {'user': user, 'active_menu': 'viewbook', 'type_list': type_list, 'book_type': book_type,
               'book_list': book_list}
    return render_to_response('viewbook.html', content, context_instance=RequestContext(req))


def viewcopies(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    id = req.GET.get('id', '')
    if id == '':
        isbn = req.GET.get('isbn', '')
        if isbn == '':
            return HttpResponseRedirect('/viewbook/')
        try:
            if not user:
                return HttpResponseRedirect('/login/')
            book = Book.objects.get(isbn=isbn)
        except:
            return HttpResponseRedirect('/viewbook/')
    else:
        try:
            if not user:
                return HttpResponseRedirect('/login/')
            bookcopy = BookCopy.objects.get(id=id)
            book = Book.objects.get(isbn=bookcopy.book.isbn)
            if bookcopy.status == 'available':
                bookcopy.status = 'borrowed'
                bookcopy.save()
                borrowinfo = BorrowInfo(bookcopy=bookcopy, user=user, BorrowDate=datetime.date.today())
                borrowinfo.save()
                book.borrowed_num += 1
                book.save()
            elif bookcopy.status == 'borrowed':
                borrowinfo = BorrowInfo.objects.get(bookcopy=bookcopy, user=user, ReturnDate=None)
                borrowinfo.ReturnDate = datetime.date.today()
                borrowinfo.save()
                bookcopy.status = 'available'
                bookcopy.save()
                book.borrowed_num -= 1
                book.save()
        except:
            return HttpResponseRedirect('/viewbook/')

    bookcopies = BookCopy.objects.filter(book=book)
    duedate_lst = []
    request_lst = []
    status_lst = []
    for copy in bookcopies:
        borrows = BorrowInfo.objects.filter(bookcopy=copy)
        reservations = Reservation.objects.filter(bookcopy=copy)
        request_lst.append(len(reservations))
        BORROW = False
        for borrow in borrows:
            if not borrow.ReturnDate:
                BORROW = True
                duedate_lst.append(borrow.BorrowDate + borrowPeriod)
                if borrow.user.user.username == user.user.username:
                    status_lst.append('my_borrow')
                else:
                    RESERVED = False
                    for res in reservations:
                        if res.user.user.username == user.user.username:
                            RESERVED = True
                            status_lst.append('my_reserved')
                            break
                    if not RESERVED:
                        status_lst.append('others_borrow')
                break

        if not BORROW:
            duedate_lst.append("")
            if not reservations:
                status_lst.append('onboard')
            else:
                status_lst.append('others_reserved')

    copy_due_req_status = zip(bookcopies, duedate_lst, request_lst, status_lst)
    content = {'user': user, 'active_menu': 'viewbook', 'book': book, 'copy_due_req_status': copy_due_req_status}
    return render_to_response('viewcopies.html', content, context_instance=RequestContext(req))


def addreservation(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    id = req.GET.get('id', '')
    if id == '':
        print id
        return HttpResponseRedirect('/viewbook/')
    try:
        bookcopy = BookCopy.objects.get(id=id)
    except:
        return HttpResponseRedirect('/viewbook/')

    resDate = datetime.date.today()
    if req.POST:
        post = req.POST
        loc = post.get('loc', '')
        dueDate = post.get('duedate', '')
        reservation = Reservation(resDate=resDate, dueDate=dueDate, bookcopy=bookcopy, user=user, status=u'处理中',
                                  loc=loc)
        reservation.save()
        return HttpResponseRedirect('/viewcopies/?isbn=bookcopy.book.isbn')

    content = {'user': user, 'active_menu': 'viewbook', 'bookcopy': bookcopy, 'resDate': resDate}
    return render_to_response('addreservation.html', content, context_instance=RequestContext(req))


def frate(x):
    return {
        'excellent': 5,
        'good': 4,
        'average': 3,
        'fair': 2,
        'poor': 1,
    }.get(x, 5)


def detail(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    isbn = req.GET.get('isbn', '')
    if isbn == '':
        return HttpResponseRedirect('/viewbook/')
    try:
        book = Book.objects.get(isbn=isbn)
    except:
        return HttpResponseRedirect('/viewbook/')

    if req.POST:
        post = req.POST
        comment = post.get('comment', '')
        now = datetime.date.today()
        eval = BookEval(book=book, user=user, evalDate=now, evalDesc=comment, rate='ex')
        eval.save()

    authors = [book.author]
    img_list = [book.img]
    book_eval = BookEval.objects.filter(book=book)
    rate_sum = 0
    rate_count = 0
    rate = 0
    for eval in book_eval:
        rate_sum = rate_sum + frate(eval.rate)
        rate_count = rate_count + 1
    if rate_count != 0:
        rate = rate_sum / rate_count
    rate_loop = ['x'] * rate
    rate_loop_empty = ['x'] * (5 - rate)
    content = {'user': user, 'active_menu': 'viewbook', 'authors': authors, 'book': book, 'book_eval': book_eval,
               'img_list': img_list, 'rate_loop': rate_loop, 'rate_loop_empty': rate_loop_empty}
    return render_to_response('detail.html', content, context_instance=RequestContext(req))


def myaccount(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
        return HttpResponseRedirect('/index/')
    borrow_num = len(BorrowInfo.objects.filter(user=user, ReturnDate=None))
    borrowhistory_num = len(BorrowInfo.objects.filter(user=user)) - borrow_num
    reservation_num = len(Reservation.objects.filter(user=user))
    content = {'user': user, 'active_menu': 'myaccount', 'borrow_num': borrow_num,
               'borrowhistory_num': borrowhistory_num, 'reservation_num': reservation_num}
    return render_to_response('myaccount.html', content)


def viewmember(req):
    username = req.session.get('username', '')
    if username != '':
        user = Librarian.objects.get(user__username=username)
    else:
        user = ''
    member_list = Librarian.objects.all()

    if req.POST:
        post = req.POST
        keywords = post.get('keywords', '')
        member_list = Librarian.objects.filter(user__username__contains=keywords)
    content = {'user': user, 'active_menu': 'viewmember', 'member_list': member_list}
    return render_to_response('viewmember.html', content, context_instance=RequestContext(req))


def modifybaseinfo(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    status = ''
    if req.POST:
        post = req.POST
        user.name = post.get('name', '')
        user.phone = post.get('phone', '')
        user.address = post.get('address', '')
        user.user.email = post.get('email', '')
        user.major = post.get('major', '')
        user.academy = post.get('academy', '')
        user.politics = post.get('politics', '')
        user.idcard = post.get('idcard', '')
        user.save()
        status = "success"
        return HttpResponseRedirect('/myaccount/')
    content = {'user': user, 'active_menu': 'myaccount', 'status': status}
    return render_to_response("modifybaseinfo.html", content, context_instance=RequestContext(req))


def reservation(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    reservation_info = Reservation.objects.filter(user=user)
    content = {'user': user, 'active_menu': 'myaccount', 'reservation_info': reservation_info}
    return render_to_response("reservation.html", content, context_instance=RequestContext(req))


def borrow(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    id = req.GET.get('id', '')
    if id:
        try:
            bookcopy = BookCopy.objects.get(id=id)
            book = Book.objects.get(isbn=bookcopy.book.isbn)
            borrowinfo = BorrowInfo.objects.get(bookcopy=bookcopy, user=user, ReturnDate=None)
            borrowinfo.ReturnDate = datetime.date.today()
            borrowinfo.save()
            bookcopy.status = 'available'
            bookcopy.save()
            book.borrowed_num -= 1
            book.save()
        except:
            return HttpResponseRedirect('/myaccount/')
    borrow_info = BorrowInfo.objects.filter(user=user, ReturnDate=None)
    Due_list = []
    Fine = []
    for borrow in borrow_info:
        Due_list.append(borrow.BorrowDate + borrowPeriod)
        if (borrow.BorrowDate + borrowPeriod) < datetime.date.today():
            d = (datetime.date.today() - (borrow.BorrowDate + borrowPeriod)).days
            Fine.append(d * 0.1)
            user.permission = 0
            user.save()
        else:
            Fine.append(0)
    zipl = zip(borrow_info, Due_list, Fine)
    now = datetime.datetime.now()
    content = {'user': user, 'active_menu': 'myaccount', 'borrow_info': borrow_info, 'Due_list': Due_list, 'zipl': zipl,
               'now': now}
    return render_to_response("borrow.html", content, context_instance=RequestContext(req))


def borrowhistory(req):
    username = req.session.get('username', '')
    if username != '':
        user = Student.objects.get(user__username=username)
    else:
        user = ''
    borrow_info = BorrowInfo.objects.filter(user=user).order_by("")
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
                Fine.append(d * 0.1)
                user.permission = 0
                user.save()
            else:
                Fine.append(0)
    zipl = zip(borrowhis, Due_list, Fine)
    now = datetime.datetime.now()
    content = {'user': user, 'active_menu': 'myaccount', 'Due_list': Due_list, 'zipl': zipl, 'now': now}
    return render_to_response("borrowhistory.html", content, context_instance=RequestContext(req))
