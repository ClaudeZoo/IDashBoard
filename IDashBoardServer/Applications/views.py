from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from Applications.models import Application
from VirtualMachines.models import VirtualMachine
import socket
import datetime, json
import random
from notifyThead import NotifyThread
# Create your views here.


def apply_new_vm(request):
    errors = []
    if request.user.is_authenticated():
        if request.method == 'POST':
            if not request.POST.get('vm_type', ''):
                errors.append('select vm_type')
            if not request.POST.get('os', ''):
                errors.append('select os')
            #if not request.POST.get('password', ''):
                #errors.append('Enter a password.')
            if not request.POST.get('memory', ''):
                errors.append('select memory')
            if not errors:
                password = request.POST.get('password', '')
                try:
                    os = request.POST.get('os', '')
                    memory = int(request.POST.get('memory', ''))
                    vm_type = request.POST.get('vm_type', '')
                    new_application = Application(type='new', vm_type=vm_type, OS=os, pwd=password, Memory=memory,
                                                  state='pending', HostName='ubuntu', applicant=request.user,
                                                  submissionTime=timezone.now())
                    new_application.save()
                except Exception, e:
                    print(e)
            else:
                return HttpResponseRedirect('/apply/')
            return HttpResponseRedirect('/applications/')
    else:
        return render_to_response('index.html', locals())


def delete_apply(request):
    errors = []
    if request.user.is_authenticated():
        if request.method == 'POST':
            if not request.body:
                errors.append('no id')
            if not errors:
                try:
                    virtualmachine = VirtualMachine.objects.get(id=int(eval(request.body)['id']))
                    new_application = Application(type='delete', state='pending', vm=virtualmachine, host=virtualmachine.vmHost,
                                                  applicant=request.user, submissionTime=timezone.now())
                    new_application.save()
                except Exception, e:
                    print(e)
            else:
                return HttpResponseRedirect('/apply/')
            return HttpResponseRedirect('/applications/')
    else:
        return render_to_response('index.html', locals())


def control_vm(request):

    errors = []
    if request.user.is_authenticated():
        if request.method == 'POST':
            control_type = request.POST['request_type']
            if not request.body:
                errors.append('no id')
            if not errors:
                try:
                    virtual_machine = VirtualMachine.objects.get(id=int(eval(request.POST['id'])))
                    new_application = Application(type=control_type, state='in_queue', vm=virtual_machine,
                                                  host=virtual_machine.vmHost, applicant=request.user,
                                                  submissionTime=timezone.now())
                    new_application.reviewer = request.user
                    new_application.save()
                    response_dict = communicate_vm_manager(new_application)
                    print(response_dict)
                    if response_dict['request_result'] == 'success':
                        new_application.state = 'done'
                        if control_type == 'start':
                            virtual_machine.state = 'online'
                        elif control_type == 'savestate':
                            virtual_machine.state = 'savestate'
                        elif control_type == 'shutdown':
                            virtual_machine.state = 'poweroff'
                        virtual_machine.save()
                    else:
                        new_application.state == response_dict['request_result']
                        new_application.error_information = response_dict['error_information']
                    new_application.save()
                except Exception, e:
                    print(e)
            else:
                return HttpResponseRedirect('/apply/')
            print(json.dumps(response_dict))
            return HttpResponse(json.dumps(response_dict))
    else:
        return render_to_response('index.html', locals())


def communicate_vm_manager(application):
    host = application.host
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host.IPAddress, host.port))
        request = {"request_id": application.id, "request_type": application.type,
                    "request_userid": application.applicant.id}
        request['vm_name'] = application.vm.hostname
        request['vm_uuid'] = application.vm.uuid
        sock.send(str(request))
        response = sock.recv(1024)
        response_dict = eval(response)
    except Exception, e:
        print e
    finally:
        application.save()
        sock.close()
        return response_dict


def get_my_applications(request):
    if request.user.is_authenticated():
        applications = request.user.applicant.all()
        my_applications = []
        for application in applications:
            try:
                dic = {
                    "id": application.id,
                    "type": application.type,
                    "applicant": application.applicant.username,
                    "parameter":
                    {
                        "os": application.OS,
                        "memory": application.Memory,
                        "vm_type": application.vm_type,
                        "hostname": application.HostName,
                        "username": application.UserName
                    },
                    "submissionTime": application.submissionTime.strftime("%Y.%m.%d %H:%M:%S"),
                    "state": application.state
                }
                if application.vm:
                    dic["parameter"]["uuid"] = application.vm.uuid
            except Exception, e:
                print e
                dic = {

                }
            finally:
                my_applications.append(dic)
        response={'data': my_applications}
        response['Access-Control-Allow-Origin'] = '*'
        return HttpResponse(json.dumps(response))
    else:
        return render_to_response('index.html', locals())


def get_untreated_applications(request):
    print(request)
    if request.user.is_authenticated():
        applications = Application.objects.filter(state='pending')
        untreated_applications = []
        for application in applications:
            try:
                dic = {
                    "id": application.id,
                    "type": application.type,
                    "applicant": application.applicant.username,
                    "parameter":
                    {
                        "os": application.OS,
                        "memory": str(application.Memory) + "M",
                        "hostname": application.HostName,
                        "username": application.UserName
                    },
                    "submissionTime": application.submissionTime.strftime("%Y.%m.%d %H:%M:%S"),
                    "treatment": "accept/refuse"
                }
                if application.vm:
                    dic["parameter"]["uuid"] = application.vm.uuid
            except Exception, e:
                print e
                dic = {
                    "id": application.id,
                    "type": application.type,
                    "applicant": application.applicant.username,
                    "parameter":
                    {
                        "hostname": application.HostName,
                        "username": application.UserName
                    },
                    "submissionTime": application.submissionTime.strftime("%Y.%m.%d %H:%M:%S"),
                    "treatment": "accept/refuse"
                }
                if application.vm:
                    dic["parameter"]["uuid"] = application.vm.uuid
            finally:
                untreated_applications.append(dic)
        response={'data': untreated_applications}
        response['Access-Control-Allow-Origin'] = '*'
        return HttpResponse(json.dumps(response))
    else:
        return render_to_response('index.html', locals())


def ratify_application(request):
    if not request.POST.get("id"):
        return HttpResponse("error")
    try:
        id = int(request.POST.get("id"))
        application = Application.objects.get(id=id)
        if application.state == 'pending':
            host = None
            vms = application.applicant.vm_user.exclude(state='deleted')
            if len(vms) == 0:
                hosts = VirtualMachine.objects.filter(uuid=None)
                host = random.sample(hosts, 1)[0]
            else:
                host = vms[0].vmHost
            application.host = host
            #print(host)
            application.state = 'in_queue'
            application.reviewer = request.user
            application.save()
            notify = NotifyThread(application) 
            notify.start()
        else:
            return HttpResponse("already treated")
    except Exception, e:
        print e
        return HttpResponse("error")
    return HttpResponse("ratified")


def ratify_all(request):
    if request.method == 'POST':
        try:
            applications = Application.objects.filter(state='pending')
            for application in applications:
                application.state = 'in_queue'
                application.reviewer = request.user
                application.save()
                notify = NotifyThread(application)
                notify.start()
        except Exception, e:
            print e
        return HttpResponse('ratified_all')


def refuse_all(request):
    if request.method == 'POST':
        try:
            applications = Application.objects.filter(state='pending')
            for application in applications:
                application.state = 'refused'
                application.reviewer = request.user
                application.save()
        except Exception, e:
            print e
    return HttpResponse('refuse_all')


def refuse_application(request):
    if not request.POST.get("id"):
        return HttpResponse("error")
    try:
        id = int(request.POST.get("id"))
        application = Application.objects.get(id=id)
        if application.state == 'refused':
            application.state = 'refused'
            application.save()
        else:
            return HttpResponse("already treated")
    except Exception, e:
        print e
        return HttpResponse("error")
    return HttpResponse("refused")


def reply_vmHost(request):
    response = {}
    response['request_id'] = request.POST['request_id']
    response['request_userid'] = request.POST['request_userid']
    response['request_type'] = request.POST['request_type']
    request_type = request.POST['request_type']
    application = Application.objects.get(id=request.POST['request_id'])
    if request.POST['request_result'] == 'success':
        vm_uuid = request.POST['vm_uuid']
        vm_name = request.POST['vm_name']
        if request_type == 'new':
            vm_username = request.POST['vm_username']
            vm_port = request.POST['port']
            same_name_vms = VirtualMachine.objects.filter(vmName=vm_name)
            same_uuid_vms = VirtualMachine.objects.filter(uuid=vm_uuid)
            if len(same_name_vms) != 0 or len(same_uuid_vms) != 0:
                response['request_response'] = 'Exist a same uuid or vmName'
                return HttpResponse(str(response))
            new_vm = VirtualMachine(uuid=vm_uuid, lastConnectTime=datetime.datetime.now(),
                                    vmName=vm_name, hostname='ubuntu', username=vm_username, state='poweroff', port=vm_port)
            new_vm.vmHost = application.host
            new_vm.vmUser = application.applicant
            new_vm.save()
            application.vm = new_vm
            application.state = 'done'
            application.save()
            response['request_response'] = 'received'
        elif request_type == 'delete':
            vm = VirtualMachine.objects.get(uuid=vm_uuid)
            vm.state = 'deleted'
            application.state = 'done'
            application.save()
            vm.save()
            response['request_response'] = 'received'
        else:
            response['request_response'] = 'type error'
    else:
        application.state = request.POST['request_result']
        application.error_information = request.POST['error_information']
        application.save()
        response['request_response'] = 'received'
        return HttpResponse(str(response))


