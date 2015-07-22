__author__ = 'wcx'

import threading
import time
import socket
from VirtualMachines.models import VirtualMachine
from Applications.models import Application
import random


class NotifyThread(threading.Thread):

    def __init__(self, application):  
        threading.Thread.__init__(self)
        self.application = application

    def run(self):
        if not self.application:
            return "no application error"
        print "start.... %s" % (self.getName(),)
        host = self.application.host
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print host.IPAddress
            sock.connect((host.IPAddress, host.port))
            request = {"request_id": self.application.id, "request_type": self.application.type,
                        "request_userid": self.application.applicant.id}
            if self.application.type == 'new':  # create
                request['vm_type'] = self.application.vm_type
            else:
                request['vm_name'] = self.application.vm.hostname
                request['vm_uuid'] = self.application.vm.uuid
            sock.send(str(request))
            #print(str(request))
            print(self.application.type)
            response = sock.recv(1024)
            response_dict = eval(response)
            if self.application.type == 'new' or self.application.type == 'delete':
                if response_dict['request_response'] == 'received' and self.application.state == 'in_queue':
                    self.application.state = 'doing'
                    #print "doing"
                else:
                    self.application.state = response_dict['request_response']
            else:
                print(response)
        except Exception, e:
            self.application.state = "Can't find VM Manager"
            print e
        finally:
            self.application.save()
            sock.close()
