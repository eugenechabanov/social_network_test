from django.contrib import admin
from .models import Post, Like
from django.contrib.admin.models import LogEntry

admin.site.register(Post)
admin.site.register(Like)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drill-down navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the results by users, content types and action flags
    list_filter = [
        'user',
        'content_type',
        'action_flag'
    ]

    # when searching the user will be able to search in both object_repr and change_message
    search_fields = [
        'object_repr',
        'change_message'
    ]

    list_display = [
        'action_time',
        'user',
        'content_type',
        'action_flag',
    ]
