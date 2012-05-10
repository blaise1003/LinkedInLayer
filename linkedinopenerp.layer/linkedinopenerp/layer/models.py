import config
from django.db import models


class Contact(models.Model):
    """Linkedin contact"""

    profile_id = models.CharField(max_length=64)
    first_name = models.CharField(max_length=1024)
    last_name = models.CharField(max_length=1024)
    headline = models.CharField(max_length=1024)
    specialties = models.CharField(max_length=1024)
    industry = models.CharField(max_length=1024)
    honors = models.CharField(max_length=1024)
    interests = models.CharField(max_length=1024)
    languages = models.CharField(max_length=1024)
    picture_url = models.CharField(max_length=1024)
    skills = models.CharField(max_length=1024)
    public_url = models.CharField(max_length=1024)
    location = models.CharField(max_length=1024)
    location_country = models.CharField(max_length=1024)

    def __unicode__(self):
        return u'%(name)s %(surname)s' % \
            {'name': self.first_name, 'surname': self.last_name}

    def update(self, vals):
        if vals['first_name']:
            self.first_name = vals['first_name']
        if vals['last_name']:
            self.last_name = vals['last_name']
        if vals['headline']:
            self.headline = vals['headline']
        if vals['specialties']:
            self.specialties = vals['specialties']
        if vals['industry']:
            self.industry = vals['industry']
        if vals['honors']:
            self.honors = vals['honors']
        if vals['interests']:
            self.interests = vals['interests']
        if vals['languages']:
            self.languages = vals['languages']
        if vals['picture_url']:
            self.picture_url = vals['picture_url']
        if vals['skills']:
            self.skills = vals['skills']
        if vals['public_url']:
            self.public_url = vals['public_url']
        if vals['location_country']:
            self.location_country = vals['location_country']
        if vals['location']:
            self.location = vals['location']


class Position(models.Model):
    """Linkedin positions

    Contact's job position included in the linkedin profile."""

    contact = models.ForeignKey(Contact)
    ref = models.CharField(max_length=1024)
    title = models.CharField(max_length=1024)
    summary = models.CharField(max_length=1024)
    start_date = models.CharField(max_length=1024)
    end_date = models.CharField(max_length=1024)
    company = models.CharField(max_length=1024)

    def __unicode__(self):
        return u'%(reference)s' % \
            {'reference': self.ref}

    def update_values(self, vals):
        if vals['title']:
            self.title = vals['title']
        if vals['summary']:
            self.summary = vals['summary']
        if vals['start_date']:
            self.start_date = vals['start_date']
        if vals['end_date']:
            self.end_date = vals['end_date']
        if vals['company']:
            self.company = vals['company']
