from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from management import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'LM.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index),
    url(r'^signup/$', views.signup),
    url(r'^login/$',views.login),
    url(r'^logout/$',views.logout),
    url(r'^setpasswd/$',views.setpasswd),
    url(r'^addbook/$',views.addbook),
    url(r'^viewbook/$',views.viewbook),
    url(r'^viewbook/detail/$',views.detail),
    url(r'^myaccount/$',views.myaccount),
    url(r'^viewmember/$',views.viewmember),
    url(r'^modifybaseinfo/$',views.midifybaseinfo),
    url(r'^reservation/$',views.reservation),
    url(r'^borrowhistory/$',views.borrowhistory),
    url(r'^borrow/$',views.borrow),
    url(r'^viewcopies/$',views.viewcopies),
    url(r'^addreservation/$',views.addreservation),
    url(r'^image/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_PATH}),
)
