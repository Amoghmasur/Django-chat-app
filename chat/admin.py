from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from .models import Thread, ChatMessage,Group,GroupMessage




admin.site.register(GroupMessage)
admin.site.register(ChatMessage)


class ChatMessage(admin.TabularInline):
    model = ChatMessage


class ThreadForm(forms.ModelForm):
    def clean(self):
        """
        This is the function that can be used to
        validate your model data from admin
        """
        super(ThreadForm, self).clean()
        first_person = self.cleaned_data.get('first_person')
        second_person = self.cleaned_data.get('second_person')

        lookup1 = Q(first_person=first_person) & Q(second_person=second_person)
        lookup2 = Q(first_person=second_person) & Q(second_person=first_person)
        lookup = Q(lookup1 | lookup2)
        qs = Thread.objects.filter(lookup)
        if qs.exists():
            raise ValidationError(f'Thread between {first_person} and {second_person} already exists.')


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread
    list_display = ['first_person','second_person','updated','timestamp']





class GroupMessage(admin.TabularInline):
    model = GroupMessage


class GroupAdmin(admin.ModelAdmin):
    inlines = [GroupMessage]
    list_display = ['name', 'display_members', 'created_at']

    def display_members(self, obj):
        return ", ".join([member.username for member in obj.members.all()])
    display_members.short_description = 'Members'



admin.site.register(Thread, ThreadAdmin)
admin.site.register(Group,GroupAdmin)

