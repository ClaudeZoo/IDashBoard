__author__ = 'daiyue'
import httplib, urllib, time
from IDBCommand.command import CommandManager
from IDBEntry.config import IDBClientConfig

httpClient = None
t = None
headers = {"Content-type": "application/x-www-form-urlencoded"
                    , "Accept": "text/plain"}
class IDBNetwork:
    config = IDBClientConfig()
    def sendCommandResult(self, api, params):
        serverHost = IDBClientConfig.getServerHost()
        serverPort = self.config.getServerPort()
        response = None
        try:
            stateHttpClient = httplib.HTTPConnection(serverHost, serverPort, timeout=30)
            stateHttpClient.request("Post", api, params, headers)
            response = stateHttpClient.getresponse()
        except Exception, e:
            print e
        finally:
            if (stateHttpClient):
                stateHttpClient.close()
            return response

    def connectServer(self):
        while(True):
            params = urllib.urlencode({'IPAddress': '127.0.0.1', 'Port': self.config.getSocketPort()})
            response = self.sendCommandResult(api = "/helloServer/", params = params)
            if response and response.status == 200:
                #execute command and send to server
                while(True):
                    cm = CommandManager()
                    result = cm.executeAutoCMD()
                    params = urllib.urlencode({"stateInfo": result, "IPAddress": '127.0.0.1'})
                    self.sendCommandResult(api = "/saveVMState/", params = params)
                    time.sleep(3)
            else:
                time.sleep(5000)
        return

    def __init__(self, p):
        self.config.setSocketPort(p)




