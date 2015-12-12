# -*- coding:utf-8 -*-

# To use mail notification, please install `apscheduler` first

from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from .models import Reservation, Student, BorrowInfo
from datetime import datetime as dt
import datetime


def run_scheduler():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(func, "interval", days=1)
    scheduler.add_job(check_overdue, "interval", days=1)
    # scheduler.add_job(send_mail_test(), "interval", minutes=1)
    scheduler.start()
    print "Scheduler started!"


def func():
    print "Hello World!"


def send_mail_test():
    send_mail("----test----", "test message here.", "henryxian@qq.com", ("Sam@163.com", ))


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
    overdue_date_list = BorrowInfo.objects.filter(ReturnDate__lt=dt.today())
    if overdue_date_list:
        for overdue_date in overdue_date_list:
            student = overdue_date.user
            mail_address = student.user.email

            #
            bookCopy_name = overdue_date.bookcopy.book.name
            bookCopy_duedate = overdue_date.ReturnDate
            send_message = u"亲爱的用户" + student + ",\n" \
                            + u"你的图书：" + bookCopy_name + "已过期，请及时归还。\n" \
                                + "应当归还的日期为：" + bookCopy_duedate
            subject = u"--------图书归还提醒--------"

            send_mail(subject, send_message, "henryxian@qq.com", (mail_address, ))