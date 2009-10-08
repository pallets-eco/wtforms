from django.db import models
from django.contrib.localflavor.us.models import USStateField

class Group(models.Model):
    name  = models.CharField(max_length=20)

    def __unicode__(self):
        return u'%s(%d)' % (self.name, self.pk)

class User(models.Model):
    username = models.CharField(max_length=40)
    group    = models.ForeignKey(Group)
    birthday = models.DateField(help_text="Teh Birthday")
    email    = models.EmailField(blank=True)
    posts    = models.PositiveSmallIntegerField()
    state    = USStateField()
    reg_ip   = models.IPAddressField("IP Addy")
    url      = models.URLField()
    file     = models.FilePathField()
    file2    = models.FileField(upload_to='.')
    bool     = models.BooleanField()
    time1    = models.TimeField()
    slug     = models.SlugField()

