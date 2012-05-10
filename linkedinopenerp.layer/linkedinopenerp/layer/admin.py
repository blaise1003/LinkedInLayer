from django.contrib import admin
from django import forms

from .models import Contact, Position

class PositionInLine(admin.TabularInline):
    """Employee's positions"""

    model = Position
    extra = 3

class ContactForm(forms.ModelForm):
    """Form for contacts"""

    class Meta:
        model = Contact

class Contacts(admin.ModelAdmin):
    """Linkedin contacts"""

    form = ContactForm
    search_fields = ['first_name', 'last_name']
    inlines = [PositionInLine]

class PositionForm(forms.ModelForm):
    """Form for position"""

    model = Position

class Positions(admin.ModelAdmin):
    """Linkedin positions"""

    form = PositionForm
    search_fields = ['ref']
    inlines = []

admin.site.register(Contact, Contacts)
admin.site.register(Position, Positions)