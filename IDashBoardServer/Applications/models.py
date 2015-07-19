from django.db import models
from django.contrib.auth.models import User
from VirtualMachines.models import VirtualMachine
# Create your models here.


class Application(models.Model):
    type = models.TextField()
    vm_type = models.TextField(null=True)
    OS = models.TextField(null=True)
    HostName = models.TextField(null=True)
    UserName = models.TextField(null=True)
    pwd = models.TextField(null=True)
    Memory = models.IntegerField(null=True)
    state = models.TextField()
    errorInformation = models.TextField(null=True)
    submissionTime = models.DateTimeField(auto_now=True, auto_now_add=False)
    applicant = models.ForeignKey(User, null=False, related_name='applicant')
    reviewer = models.ForeignKey(User, null=True, related_name='reviewer')
    vm = models.ForeignKey(VirtualMachine, null=True, related_name='vm')
    host = models.ForeignKey(VirtualMachine, null=True, related_name='host')