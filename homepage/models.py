from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.conf import settings
from datetime import date, datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from time import gmtime, strftime, strptime

# citation for profile model:
# title: Django custom user profile
# code: code is written in python and html
# url: https://ordinarycoders.com/django-custom-user-profile

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @receiver(post_save, sender=User)  # if a User is created, create a Profile as well
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)  # if a User is saved, save a Profile as well
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


class CourseModel(models.Model):
    # Database refused to remove profile id and current profile id so i used fake migrations and added the fields

    # title: Fix 'column already exists' Django Migration Error?
    # date: august 1, 2017
    # code: code is written in python
    # url: https://stackoverflow.com/questions/45445082/fix-column-already-exists-django-migration-error
    profile_id = models.CharField(max_length=200, default='')
    owner_profile = models.ForeignKey(Profile, null=True, related_name='schedule_owner', on_delete=models.CASCADE)
    # title: Django models avoid duplicates
    # date: june 16, 2010
    # code: code is written in python and html
    # url: https://stackoverflow.com/questions/3052975/django-models-avoid-duplicates
    # Used this to avoid duplicate coursemodels
    class_num = models.CharField(max_length=200, default='')  # 5 digit code
    course_sect = models.CharField(max_length=200, default='')  # course_section like 001
    course_title = models.CharField(max_length=200, default='')  # e.g. Introduction to CS
    course_acronym = models.CharField(max_length=200, default='')  # e.g. CS 1110
    course_days = models.CharField(max_length=200, default='')  # e.g. MoTu
    course_type = models.CharField(max_length=200, default='')  # e.g. LEC
    course_time = models.CharField(max_length=200, default='')
    course_day_and_time = models.CharField(max_length=200, default='')
    course_instructor = models.CharField(max_length=200, default='')
    course_enrolled = models.CharField(max_length=200, default='')
    course_waitlisted = models.CharField(max_length=200, default='')
    location = models.CharField(max_length=200, default='')
    locations = models.CharField(max_length=200, default='')
    credit = models.IntegerField(default=3)

    def get_course_day_and_time_as_list(self):
        return self.course_day_and_time.split(";")

    # title: Django Migrations removing field
    # date: may 29, 2017
    # code: code is written in python
    # url: https://stackoverflow.com/questions/44247985/django-migrations-removing-field

    # this method allowed me to actually remove classNum field from model, migrations.remove() went to object
    # instead of trying to find the field inside the model
    @property
    def classNum(self):
        pass

    def __str__(self):
        return self.class_num


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', null=True)
    name = models.CharField(max_length=80)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


class ListModel(models.Model):
    class_number = models.CharField(max_length=200)
    classNum = models.CharField(max_length=200)

    def __str__(self):
        return self.classNum

# citation for adding friends:
# title: Step by Step guide to add friends with Django
# author: "Abhik"
# date: october 25, 2020
# code: code is written in python and html
# url: https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d

# title: How to Create a Friend Request Model in Django
# author: 'Moeedlodhi'
# date: april 5, 2021
# code: code written in python
# url: https://python.plainenglish.io/creating-a-friend-request-model-in-django-640257b2c67f
class Friend(models.Model):
    users = models.ManyToManyField(Profile)
    current_user = models.ForeignKey(Profile, related_name='owner', on_delete=models.CASCADE, null=True)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.add(new_friend)

    @classmethod
    def delete_friend(cls, current_user, friend_to_be_deleted):
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.remove(friend_to_be_deleted)


class FriendRequest(models.Model):
    sender = models.ForeignKey(Profile, null=True, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Profile, null=True, related_name='receiver', on_delete=models.CASCADE)


class Event(models.Model):
    title = models.CharField(max_length=200)  # I'll use this as e.g. CS 1110
    description = models.CharField(max_length=400)  # and use this as e.g. Introduction to CS
    start_time = models.CharField(max_length=200, default='')
    end_time = models.CharField(max_length=200, default='')
    start_time_as_time_object = models.CharField(max_length=200, default='')
    end_time_as_time_object = models.CharField(max_length=200, default='')
    day = models.CharField(max_length=200, default='')  # e.g. Mo
    unique_num = models.CharField(max_length=200, null=True)  # 5 digit code
    location = models.CharField(max_length=200, null=True)
    course = models.ForeignKey(CourseModel, related_name='course', on_delete=models.CASCADE, null=True)
    owner = models.ForeignKey(Profile, related_name='owner_profile', on_delete=models.CASCADE, null=True)

    # citation for algorithm for overlap checking
    # title: Django Calendar
    # author: 'alexpnt'
    # date: may 21, 2019
    # code: code written mainly in python and html
    # url: https://github.com/AlexPnt/django-calendar
    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:  # edge case
            overlap = False
        elif (fixed_start <= new_start <= fixed_end) or \
                (fixed_start <= new_end <= fixed_end):  # inner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end:  # outer limits
            overlap = True
        return overlap

    def clean(self):
        end_time = strptime(self.end_time_as_time_object, "%H.%M.%S.000000%z")
        start_time = strptime(self.start_time_as_time_object, "%H.%M.%S.000000%z")
        if end_time <= start_time:
            raise ValidationError('Ending hour must be after the starting hour')

        events = Event.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                event_start_time = strptime(event.start_time_as_time_object, "%H.%M.%S.000000%z")
                event_end_time = strptime(event.end_time_as_time_object, "%H.%M.%S.000000%z")
                if self.check_overlap(event_start_time, event_end_time, start_time, end_time):
                    raise ValidationError(
                        'There is an overlap with another class: ' + str(event.title) + " at " +
                        str(event.start_time) + ' - ' + str(event.end_time) + ", " + str(event.day))
