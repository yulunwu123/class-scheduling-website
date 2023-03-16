from django.urls import path, reverse_lazy

from . import views
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView, PasswordChangeView, \
    PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView

from .views import CustomLoginView

app_name = 'homepage'

urlpatterns = [
    # ex: /(because included in hooslist/urls.py) or /homepage
    path('', views.index, name='home'),
    path('department/<str:department>', views.department, name='department'),
    path('search', views.search, name='search'),
    path('searchfriend', views.searchfriend, name='searchfriend'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('login', CustomLoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('password_change', PasswordChangeView.as_view(success_url=reverse_lazy('homepage:password_change_done')),
         name='password_change'),
    # path('password_change', PasswordChangeView.as_view(),
    #      name='password_change'),
    path('password_change/done', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset', PasswordResetView.as_view(success_url=reverse_lazy("homepage:password_reset_done")),
         name='password_reset'),
    path('password_reset/done', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>', PasswordResetConfirmView.as_view(success_url=
        reverse_lazy("homepage:password_reset_complete")), name='password_reset_confirm'),
    path('reset/done', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('create_account', views.register, name='register'),
    path('edit', views.edit, name='edit'),
    path('addtolist', views.addToList, name='addtolist'),
    path('removefromlist', views.addToList, name='removefromlist'),
    path('friendslist', views.friendslist, name='friendslist'),
    path('schedule_builder/<int:userID>', views.view_schedule, name='schedule_builder'),
    path('send_friend_request/<int:userID>', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:requestID>', views.accept_friend_request, name='accept_friend_request'),
    path('delete_friend/<int:userID>', views.remove_friend, name='delete_friend'),
    path('cancel_friend_request/<int:requestID>', views.cancel_friend_request, name='cancel_friend_request'),
    path('test', views.showSchedule,name='show_schedule'),
    path('schedule_builder/delete_event/<int:eventID>', views.delete_event, name='delete_event'),
]
