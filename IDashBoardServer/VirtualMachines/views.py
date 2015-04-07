from django.shortcuts import render
from django.http import HttpResponse
from VirtualMachines.models import VirtualMachine
import time, datetime
from django.contrib.sessions.models import Session
import json

# Create your views here.

def VMState(request):
    if 'IPAddress' in request.POST and request.POST['IPAddress']:
        ip = request.POST['IPAddress']
        try:
            vm = VirtualMachine.objects.filter(IPAddress= ip)
            if len(vm) == 0:
                return HttpResponse('error')
        except:
            return HttpResponse('error')
    if 'stateInfo' in request.POST and request.POST['stateInfo']:
        stateInfo = request.POST['stateInfo']
        vm[0].stateInfo = stateInfo
        vm[0].lastConnectTime = datetime.datetime.now()
        info = eval(request.POST['stateInfo'])
        vm[0].updateInfo(info)
        vm[0].save()
        #encode = json.dumps(eval(request.POST['stateInfo']))
        #print encode["HostName"]
    t = datetime.datetime.now()
    s = Session.objects.filter(expire_date__gte = t)
    response = HttpResponse()
    if len(s) != 0:
        response["content"] = "someone"
    else:
        response.write("noone")
        response["content"] = "noone"#response['person'] = "noone"
    return response

def helloServer(request):
    if 'IPAddress' in request.POST and request.POST['IPAddress'] and 'Port' in request.POST and request.POST['Port']:
        ip = request.POST['IPAddress']
        port = request.POST['Port']
        print datetime.datetime.now()
        try:
            vm = VirtualMachine.objects.filter(IPAddress= ip)
            if len(vm) != 0:
                vm[0].lastConnectTime = datetime.datetime.now()
                vm[0].port = port
                vm[0].save()
            else:
                newVM = VirtualMachine(IPAddress= ip, port= port, lastConnectTime = datetime.datetime.now())
                newVM.save()
        except Exception, e:
            print e
            return
    else:
        return
    #return HttpResponse(json.dumps({"haha":"Hello world"}))
    r = HttpResponse()
    r.write("hello world")
    r["content"] = "helloworld"
    #return HttpResponse("hello world")
    return r
