# -*- coding:utf-8 -*-

# To use mail notification, please install `apscheduler` first

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from management.models import *
from datetime import datetime as dt
import datetime
from management.choice import *

def run_scheduler():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(func, "interval", days=1)
    scheduler.add_job(check_overdue, "interval", days=1)
   # scheduler.add_job(send_mail_test(), "interval", minutes=1)
    scheduler.start()
    print "Scheduler started!"

def func():
    print "Hello World!"

def reservation_mail_notificaiton(res):
    subject = u"预约满足通知"
    send_message = u"亲爱的"+res.user.name+":\n"+u"你预约的《"+res.bookcopy.book.name+u"》图书已到,请到"+\
                   res.take_loc+u"借阅。\n\n"+u"预约保留截止日期："+(res.satisfyDate+reservedPeriod).strftime("%Y-%m-%d")
    mail_address = res.user.user.email
    print "send email to",mail_address
    send_mail(subject,send_message,"1935003573@qq.com",(mail_address,))

def send_mail_test():
#    send_mail("----test----", "test message here.", "henryxian@qq.com", ("Sam@163.com", ))
    send_mail("----test----", "test message here.", "1935003573@qq.com", ("gzlyp2011@163.com", ))

# ignore this one
def check_overdue2():
    time_delta = datetime.timedelta(days=5)
    # due_date_set = Reservation.objects.filter(dueDate__lt=timezone.now())
    due_date_list = Reservation.objects.filter(dueDate__lt=dt.now())
    if due_date_list:
        for due_date in due_date_list:
            # mail_address = Student.user.email
            student = due_date.user
            mail_address = student.user.email

            # send_mail("subject here", "here is the message",
            #           "from... ", "to...", fail_silently=False)

            bookCopy_name = due_date.bookcopy.book.name
            bookCopy_dueDate = due_date.dueDate
            send_message = u"亲爱的用户" + student + ",\n" \
                            + "你的图书：" + bookCopy_name + "已过期，请及时归还。\n" \
                                + "应当归还的日期为：" + bookCopy_dueDate
            subject = u"--------图书归还提醒--------"
            send_mail(subject, send_message, "henryxian@qq.com", (mail_address, ))


            # send_mail("----test----", "test message here",
            #           "henryxian@qq.com", (mail_address,))


# check the borrowinfo to see if the borrowed book is returned before the due date.
# If not, send an email to notify him/her.
def check_overdue():
    # remindPeriod = datetime.timedelta(5)
    not_return_list = BorrowInfo.objects.filter(ReturnDate=None)
    overdue_date_list = []
    for borrow in not_return_list:
        if borrow.BorrowDate+borrowPeriod < dt.today():
            overdue_date_list.append(borrow)
    if overdue_date_list:
        for overdue_date in overdue_date_list:
            student = overdue_date.user
            mail_address = student.user.email
            bookCopy_name = overdue_date.bookcopy.book.name
            bookCopy_duedate = overdue_date.BorrowDate+borrowPeriod
            send_message = u"亲爱的用户" + student + ",\n" \
                            + u"你的图书：" + bookCopy_name + "已过期，请及时归还。\n" \
                                + "应当归还的日期为：" + bookCopy_duedate
            subject = u"--------图书归还提醒--------"

            send_mail(subject, send_message, "1935003573@qq.com", (mail_address, ))