from .models import Profile, \
    FriendRequest, Event, Friend, CourseModel, Comment
from django.contrib import admin


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']


admin.site.register(Event)
admin.site.register(Friend)
admin.site.register(FriendRequest)
admin.site.register(CourseModel)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'body', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)
