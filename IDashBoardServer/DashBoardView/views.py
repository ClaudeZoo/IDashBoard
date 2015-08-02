from django.shortcuts import render, render_to_response
from django import template
from VirtualMachines.models import VirtualMachine
import datetime, time, json, string
from django.http import HttpResponse, HttpResponseRedirect
from DashBoardUser.models import DashBoardUser
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.db.models import Q
import pytz
# Create your views here.


def home(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('home.html',locals())
    else:
        return render_to_response('index.html', locals())


def detail(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('detail.html', locals())
    else:
        return render_to_response('index.html')



def settings(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        u = User.objects.filter(id=request.user.id)
        if len(u) != 0:
            try:
                profile = u[0].dashboarduser
            except:
                profile = DashBoardUser(user=u[0])
                profile.save()

            username = u[0].username
            email = u[0].email
            if profile.phone:
                phone = profile.phone
            if profile.department:
                department = profile.department.encode('utf-8')
            return render_to_response('settings.html', locals())

    return render_to_response('index.html')


def get_detail(request, vm_id):
    if request.user.is_authenticated():
        vmDetail = {}
        #vm_id = 1
        try:
            vm = VirtualMachine.objects.filter(id=vm_id)
            if len(vm) != 0:
                vmDetail = {'data': vm_id, 'Access-Control-Allow-Origin': '*'}
                vmDetail['uName'] = vm[0].osInfo[0:-8]
                vmDetail['cpuInfo'] = vm[0].cpuInfo
                vmDetail['memory'] = vm[0].mem
                vmDetail['swap'] = vm[0].swap
                vmDetail['cpuLoad'] = vm[0].percentCPU
                vmDetail['tasks'] = vm[0].tasks
                vmDetail['userName'] = vm[0].username
                vmDetail['ipv4'] = vm[0].inet4
                vmDetail['ipv6'] = vm[0].inet6
                vmDetail['broadcast'] = vm[0].bcast
                vmDetail['mask'] = vm[0].mask
                vmDetail['dns'] = vm[0].DNS
                vmDetail['process'] = []
                if len(vm[0].process) != 0:
                    process = vm[0].process.split("\n")
                    pinfodic = {}
                    for p in process:
                        pinfo = p.split()
                        if len(pinfo) < 12:
                            break
                        pinfodic['PID'] = pinfo[0]
                        pinfodic['USER'] = pinfo[1]
                        pinfodic['cpu'] = pinfo[8]
                        pinfodic['mem'] = pinfo[9]
                        pinfodic['cmd'] = pinfo[11]
                        vmDetail['process'].append(pinfodic.copy())
                #vmDetail['process'] = [{'PID':'1112','USER':'root', 'cpu': '21.7', 'mem':'3.1', 'cmd':'Xorg'},\
                 #   {'PID':'32376','USER':'wcx', 'cpu': '21.7', 'mem':'0.1', 'cmd':'top'}]
            else:
                vmDetail = {'IPAddress': [], 'stateInfo': []}
        except Exception, e:
            print e
            return HttpResponse(e)
        return HttpResponse(json.dumps(vmDetail))
    return render_to_response('index.html', locals())


def RefreshHomePage(request):
    if request.user.is_authenticated():
        ActiveVMs = getAllActiveVMs()
        response = {'ActiveVMs': ActiveVMs}
        response['Access-Control-Allow-Origin'] = '*'
        return HttpResponse(json.dumps(response))
    else:
        return render_to_response('index.html', locals())


def RefreshSimplePage(request):
    if request.user.is_authenticated():
        ActiveVMs = getAllActiveVMsSimple()
        response = {'data': ActiveVMs}
        response['Access-Control-Allow-Origin'] = '*'
        return HttpResponse(json.dumps(response))
    else:
        return render_to_response('index.html', locals())


def RefreshSimplePageHost(request):
    if request.user.is_authenticated():
        ActiveVMs = getAllActiveVMsSimpleHost()
        response = {'data': ActiveVMs}
        response['Access-Control-Allow-Origin'] = '*'
        return HttpResponse(json.dumps(response))
    else:
        return render_to_response('index.html', locals())


def VMDetails(request, ip):
    vmDetail = {}
    try:
        vm = VirtualMachine.objects.filter(IPAddress=ip)
        if len(vm) != 0:
            vmDetail = {'IPAddress': vm[0].IPAddress, 'stateInfo': eval(vm[0].stateInfo)}
        else:
            vmDetail = {'IPAddress': [], 'stateInfo': []}
    except Exception, e:
        print e
        return
    return HttpResponse(json.dumps(vmDetail))


def getAllActiveVMsSimpleHost():
    t = datetime.datetime.now()
    t -= datetime.timedelta(seconds=60)
    #vms = VirtualMachine.objects.filter(lastConnectTime__gte = t)
    vms = VirtualMachine.objects.filter(uuid=None)
    ActiveVMs = []
    for vm in vms:
        if vm.IPAddress == '10.0.0.121':
            disk_used = get_host2_disk_used(vm.disk)
        else:
            disk_used = get_host1_disk_used(vm.disk)
        try:
            dic = {
                'state': 'online',
                'ip': vm.IPAddress,
                'wan_ip': vm.WANIP,
                'os': vm.osInfo[0:-8],
                'Disk': disk_used,
                'Memory': str(int(float(vm.mem.split()[1].rstrip('k')) / float(vm.mem.split()[0].rstrip('k')) * 100 + 0.5)) + '%',
                'CPU': str(int(100 - float(vm.percentCPU.split()[3].split('%')[0]) + 0.5)) + '%',
                'id': vm.id
            }
        except Exception, e:
            dic = {
                'state': 'online',
                'ip': vm.IPAddress,
                'wan_ip': vm.WANIP,
                'os': vm.osInfo,
                'Disk': '0%',
                'Memory': '0%',
                'CPU': '0%',
                'id': vm.id
            }
        finally:
            if vm.lastConnectTime < t:
                dic['state'] = "offline"
            ActiveVMs.append(dic)
    return ActiveVMs


def getAllActiveVMsSimple():
    t = datetime.datetime.now()
    t -= datetime.timedelta(seconds=60)
    #vms = VirtualMachine.objects.filter(lastConnectTime__gte = t)
    vms = VirtualMachine.objects.filter(~Q(uuid=None), ~Q(state='deleted'))
    ActiveVMs = []
    for vm in vms:
        dict = {}
        disk_used = get_disk_used(vm.disk)
        try:
            dic = {
                'state': 'online',
                'ip': vm.IPAddress,
                'wan_ip': vm.WANIP,
                'port': vm.port,
                'os': vm.osInfo[0:-8],
                'vm_name': vm.vmName,
                'Disk': disk_used,
                'Memory': str(int(float(vm.mem.split()[1].rstrip('k')) / float(vm.mem.split()[0].rstrip('k')) * 100 + 0.5)) + '%',
                'CPU': str(int(100 - float(vm.percentCPU.split()[3].split('%')[0]) + 0.5)) + '%',
                'id': vm.id
            }
        except Exception, e:
            print(e)
            print('hehe')
            dic = {
                'state': 'online',
                'ip': vm.IPAddress,
                'wan_ip': vm.WANIP,
                'port': vm.port,
                'os': vm.osInfo,
                'vm_name': vm.vmName,
                'Disk': '0%',
                'Memory': '0%',
                'CPU': '0%',
                'id': vm.id
            }
        finally:
            if vm.lastConnectTime < t:
                dic['state'] = "offline"
            ActiveVMs.append(dic)
    return ActiveVMs


def get_disk_used(disk_info):
    disk_list = disk_info.split()
    used = 0
    size = 0
    if (len(disk_list) - 7) % 6 == 0:
        disk_number = (len(disk_list) - 7) / 6
        for index in range(1, disk_number):
            size_info = disk_list[index*6 + 2]
            if size_info[-1] == 'K':
                size += float(size_info[:-1])
            elif size_info[-1] == 'M':
                size += float(size_info[:-1]) * 1024
            elif size_info[-1] == 'G':
                size += float(size_info[:-1]) * 1024 * 1024
            else:
                size += 0
            used_info = disk_list[index*6 + 3]
            if used_info[-1] == 'K':
                used += float(used_info[:-1])
            elif used_info[-1] == 'M':
                used += float(used_info[:-1]) * 1024
            elif used_info[-1] == 'G':
                used += float(used_info[:-1]) * 1024 * 1024
            else:
                used += 0
    return str(int(100 * used / size + 0.5)) + '%'


def get_host1_disk_used(disk_info):
    disk_list = disk_info.split()
    used = 0
    size = 0
    if (len(disk_list) - 9) % 6 == 0:
        disk_number = (len(disk_list) - 9) / 6
        for index in range(1, disk_number+1):
            size_info = disk_list[index*6 + 4]
            if size_info[-1] == 'K':
                size += float(size_info[:-1])
            elif size_info[-1] == 'M':
                size += float(size_info[:-1]) * 1024
            elif size_info[-1] == 'G':
                size += float(size_info[:-1]) * 1024 * 1024
            else:
                size += 0
            used_info = disk_list[index*6 + 5]
            if used_info[-1] == 'K':
                used += float(used_info[:-1])
            elif used_info[-1] == 'M':
                used += float(used_info[:-1]) * 1024
            elif used_info[-1] == 'G':
                used += float(used_info[:-1]) * 1024 * 1024
            else:
                used += 0
    return str(int(100 * used / size + 0.5)) + '%'


def get_host2_disk_used(disk_info):
    disk_list = disk_info.split()
    used = 0
    size = 0
    if (len(disk_list) - 7) % 6 == 0:
        disk_number = (len(disk_list) - 7) / 6
        for index in range(1, disk_number+1):
            size_info = disk_list[index*6 + 2]
            if size_info[-1] == 'K':
                size += float(size_info[:-1])
            elif size_info[-1] == 'M':
                size += float(size_info[:-1]) * 1024
            elif size_info[-1] == 'G':
                size += float(size_info[:-1]) * 1024 * 1024
            else:
                size += 0
            used_info = disk_list[index*6 + 3]
            if used_info[-1] == 'K':
                used += float(used_info[:-1])
            elif used_info[-1] == 'M':
                used += float(used_info[:-1]) * 1024
            elif used_info[-1] == 'G':
                used += float(used_info[:-1]) * 1024 * 1024
            else:
                used += 0
    return str(int(100 * used / size + 0.5)) + '%'


def getAllActiveVMs():
    t = datetime.datetime.now()
    t -= datetime.timedelta(seconds=60)
    vms = VirtualMachine.objects.filter(lastConnectTime__gte = t)
    ActiveVMs = []
    for vm in vms:
        dic = {'IPAddress': vm.IPAddress, 'stateInfo': eval(vm.stateInfo)}
        ActiveVMs.append(dic)
    return ActiveVMs


def apply(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('apply.html', locals())
    else:
        return render_to_response('index.html', locals())


def audit(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('audit.html', locals())
    else:
        return render_to_response('index.html', locals())


def applications(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('applications.html', locals())
    else:
        return render_to_response('index.html', locals())


def myVMs(request):
    if request.user.is_authenticated():
        t = Group.objects.filter(name='teachers')[0]
        isTeacher = t in request.user.groups.all()
        return render_to_response('myVMs.html', locals())
    else:
        return render_to_response('index.html', locals())


def login(request):
    errors = []
    if request.method == 'POST':
        if not request.POST.get('username', ''):
            errors.append('Enter a subject.')
        if not request.POST.get('password', ''):
            errors.append('Enter a message.')
        if not errors:
            username = request.POST.get('username','')
            password = request.POST.get('password','')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')
    return HttpResponseRedirect('/')


def logout(request):
    auth.logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect("/")
