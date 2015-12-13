#coding:utf8

import re
import sys
import os
import os.path
import codecs
import datetime,time
import random
import chardet
import django.contrib.auth.models as auth
from management.models import *

path = "/home/liyanp/dbproject/Jack/Library-Management/data/"

imagepath = "/home/liyanp/dbproject/Jack/Library-Management/bookimage/image1/"

ens = re.compile(u"[)a-zA-Z0-9-_(\s]+")
w = re.compile(u"[（）]")
chs = re.compile(u"\W+")
noise = re.compile(u"[,'#?，:&;\.\[\]]")


def toUnicode(text):
    if isinstance(text, str):
        encoding=chardet.detect(text)['encoding']
        return text.decode(encoding,"ignore")
    return text

def get_bookinfo():
    print "get book info"
    authors = []
    publihsers = []
    names = []
    typs = []
    pubDates = []
    isbns = []
    descs = []
    imgs = []
    for parent,dirnames,filenames in os.walk(path):
        for dirname in dirnames:
            bookdir = os.path.join(parent,dirname)
            for file in os.listdir(bookdir):
                img_name = file+dirname+".jpg"
                filepath = os.path.join(bookdir,file)
                f = open(filepath,'r')
                contents = f.read()
                contents = toUnicode(contents)
                fields = contents.split('\n')
                if len(fields)==7:
                    names.append(fields[0])
                    typs.append(fields[2])
                    pubDates.append(fields[4])
                    isbns.append(fields[5])
                    descs.append(fields[6])
                    authors.append(fields[1])
                    publihsers.append(fields[3])
                    imgs.append(img_name)

    return authors,publihsers,names,typs,pubDates,isbns,descs,imgs


def gen_authors(authors):
    print "generate authors"
    # Author.objects.all().delete()
    id = 1
    authors = set(authors)
    for author_name in authors:
        author = Author(author_id=id,name=author_name,email=u"".join(author_name.split())+"@163.com")
        try:
            author.save()
            id = id+1
        except:
            continue

def gen_publishers(publishers):
    print "gengerate publishers"
    # Publisher.objects.all().delete()
    pub_id = 1
    ads = [u"广州",u"北京",u"上海"]
    publishers = set(publishers)
    for i,publisher_name in enumerate(publishers):
        publisher = Publisher(name=publisher_name,publisher_id=pub_id,
                              address=ads[i%len(ads)],website="http://www."+u"".join(publisher_name.split())+".com")
        try:
            publisher.save()
            pub_id+=1
        except:
            continue

def gen_book(authors,publihsers,names,typs,pubDates,isbns,descs,imgs):
    print "generate books"
    type = ["A","B","C","D","E","F","G","H","I","J","K","L","N","M","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
    for i in range(len(names)):
        author = Author.objects.get(name=authors[i])
        publihser = Publisher.objects.get(name=publihsers[i])
        t = time.strptime(pubDates[i],"%Y-%m-%d")
        y,m,d = t[0:3]
        pubDate = datetime.date(y,m,d)
        copies_num = random.randint(1, 3)
        borrowed_num = random.randint(0, copies_num)
        typ = ens.sub(u"",typs[i])
        typ = noise.sub(u"",w.sub(u"",typ))
        name = noise.sub(u"",ens.sub(u"",names[i]))
        if len(name)<4:
            name = ens.search(names[i]).group()
        img = "image/"+imgs[i]
        call_number = type[random.randint(0,25)]+type[i%26]+str(i%135)+"/"+str((i+25)%99)
        book = Book(isbn=isbns[i],name=name,typ=typ,img=img,author=author,pubDate=pubDate,\
                    publisher=publihser,copies_num=copies_num,borrowed_num=borrowed_num,desc=descs[i],call_number=call_number)
        try:
            book.save()
        except:
            continue

def gen_bookcopy():
    print "generate bookcopy"
    book = Book.objects.all()
    barcode = 6900000000
    collection_loc = [u'东校区流通',u'北校区流通',u'南校区流通',u'珠海校区流通']
    id = 1
    for b in book:
        for i in range(b.borrowed_num):
            bookcopy = BookCopy(book=b,copy_id=id,barcode=str(barcode+id),status="borrowed",collection_loc=collection_loc[i%len(collection_loc)])
            bookcopy.save()
            id+=1
        for j in range(b.copies_num-b.borrowed_num):
            bookcopy = BookCopy(book=b,copy_id=id,barcode=str(barcode+id),status="available",collection_loc=collection_loc[j%len(collection_loc)])
            bookcopy.save()
            id+=1


def add_group(groups=[u"图书管理员",u"学生"]):
    print "adding group"
    for name in groups:
        try:
            g = auth.Group(name=name)
            g.save()
        except:
            continue

def gen_user(n =100):
    print "generate user"
    sid = 15213000
    group = auth.Group.objects.get(name=u'学生')
    name = [u"张",u"李",u"王",u"黎",u"陈"]
    education = [u"本科",u"硕士",u"博士"]
    politics = [u"党员",u"团员"]
    major = [u"计算机技术",u"软件工程",u"计算机科学与技术",u"电子"]
    academy = [u"数据科学与计算机学院",u"软件学院",u"超算学院",u"信息科学与技术学院"]
    address = [u"至善园",u"明德园",u"慎思园"]
    phoneid = 1000
    print "adding student"
    for i in range(n):
        try:
            s_id = str(sid+i)
            user = auth.User(username=s_id,email="gzlyp2011@163.com")
            user.set_password(123456)
            try:
                user.save()
                group.user_set.add(user)
            except:
                user = auth.User.objects.get(username=s_id)

            stu = Student(user=user,phone="1358050"+str(phoneid+i),address=u"中山大学"+address[i%len(address)],\
                name=name[i%len(name)]+str(i),education=education[i%len(education)],\
                major=major[i%len(major)],academy=academy[i%len(academy)],politics=politics[i%len(politics)],idcard="44098119930122"+str(phoneid+i))
            stu.save()

        except Exception as e:
            print e
            continue

    group = auth.Group.objects.get(name=u'图书管理员')
    tid = 1000
    name = [u"黄",u"林",u"杨"]
    loc = [u'东校区流通',u'北校区流通',u'南校区流通',u'珠海校区流通']
    print "adding librarian"
    for i in range(n/5):
        try:
            t_id = str(tid+i)
            user = auth.User(username=t_id,email="187501"+str(tid+i)+"@qq.com")
            user.set_password(123456)
            try:
                user.save()
                group.user_set.add(user)
            except:
                user = auth.User.objects.get(username=t_id)
            lib = Librarian(user=user,phone="1358060"+str(phoneid+i),address=u"中山大学",\
                name=name[i%len(name)]+str(i),loc=loc[i%len(loc)])
            lib.save()
        except Exception as e:
            print e
            continue

def gen_borrowinfo():
    print "generate borrow info"
    bookcopy = BookCopy.objects.filter(status="borrowed")
    abookcopy = BookCopy.objects.filter(status="available")
    student = Student.objects.all()[:40]
    id = 1
    for i,bc in enumerate(bookcopy):
        borrowinfo = BorrowInfo(bookcopy=bc,borrow_id=id,user=student[i%len(student)],BorrowDate=datetime.date(2015,11,i%30+1))
        try:
            borrowinfo.save()
            id = id+1
        except Exception as e:
            print e
            continue

    for i,bc in enumerate(abookcopy):
        m = random.randint(1,11)
        borrowinfo = BorrowInfo(bookcopy=bc,user=student[i%len(student)],
                                BorrowDate=datetime.date(2015,m,i%28+1),ReturnDate=datetime.date(2015,m+1,20))
        try:
            borrowinfo.save()
        except Exception as e:
            print e
            continue

def gen_reservation():
    print "generate reservation"
    Reservation.objects.all().delete()
    period = datetime.timedelta(days=30)
    delay = datetime.timedelta(days=10)
    bookcopy = BookCopy.objects.filter(status="borrowed")
    abookcopy = BookCopy.objects.filter(status="available")
    student = Student.objects.all()[:20]
    id = 1
    loc = [u'东校区流通',u'北校区流通',u'南校区流通',u'珠海校区流通']
    for i,bc in enumerate(bookcopy):
        r = random.randint(1,2)
        if r==2:
            borrow = BorrowInfo.objects.filter(bookcopy=bc)
            for b in borrow:
                if b.user.user.username != student[i%len(student)].user.username:
                    resDate=b.BorrowDate+delay
                    reservation = Reservation(bookcopy=bc,user=student[i%len(student)],resDate=resDate,dueDate=resDate+period,
                                              status=u"处理中",take_loc = loc[i%len(loc)],res_id=id)
                    try:
                        reservation.save()
                        id = id + 1
                    except Exception as e:
                        print e
                        continue

    for i,bc in enumerate(abookcopy):
        r = random.randint(1,2)
        if r == 2:
            take_loc = list(loc)
            take_loc.remove(bc.collection_loc)
            resDate = datetime.date(2015,11,random.randint(15,30))
            reservation = Reservation(bookcopy=bc,user=student[i%len(student)],resDate=resDate,dueDate=resDate+period,\
                                      status=u"处理中",take_loc=take_loc[i%len(take_loc)],res_id=id)
            try:
                reservation.save()
                id += 1
            except:
                print e
                continue

def gen_bookeval():
    print "generate book evaluation"
    book = Book.objects.all()
    student = Student.objects.all()
    rate = ['excellent','good','average','fair','poor']
    content = [u"这本书真的很好！",u"内容由浅入深，讲解形象通俗易懂",u"值得一看"]
    id = 1
    for i,b in enumerate(book):
        for j in range(len(content)):
            bookeval = BookEval(book=b,eval_id=id,user=student[i%len(student)],rate=rate[random.randint(0,len(rate)-1)],evalDesc=content[i%len(content)],\
                            evalDate=datetime.date(2015,random.randint(1,12),random.randint(1,28)))
            try:
                bookeval.save()
                id = id+1
            except Exception as e:
                print e
                continue


def gen_notification(n=5):
    print "generate notificaiton"
    Notification.objects.all().delete()
    title = [u"新书上架",u"热书推荐",u"借阅须知"]
    person = [u"张小明",u"黄灵",u"陈小东",u"吴名"]
    for i in range(n):
        notification = Notification(pub_person=person[i%len(person)],title=title[i%len(title)],
                                    time=datetime.datetime(2015,(i+1)%12,20),content=u"通知通知"*10)
        try:
            notification.save()
        except:
            continue

def main():
    # reload(sys)
    # sys.setdefaultencoding("utf8")
    authors,publihsers,names,typs,pubDates,isbns,descs,imgs = get_bookinfo()
    gen_authors(authors)
    gen_publishers(publihsers)
    gen_book(authors,publihsers,names,typs,pubDates,isbns,descs,imgs)
    gen_bookcopy()
    add_group()
    gen_user()
    gen_borrowinfo()
    gen_reservation()
    gen_bookeval()
    gen_notification()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LM.settings")
    main()
