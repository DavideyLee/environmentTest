#coding: UTF-8

import paramiko
import os
import redis
import socket
import win32com.client
import logging
import MonitorConfig

# Linux System
class LinuxServer():
    '''Monitor linux server and output message
       ssh to other server cmd messge
       check file exist
       check service exist
    '''
    def __init__(self, server):
        self.hostname = server['hostname']
        self.username = server['username']
        self.password = server['password']
        self.sshport = server['sshport']

            
    #SSH连接函数
    def ssh_cmd(self, cmd):
        result = ""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.hostname, self.sshport, self.username, self.password, timeout=3)
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read()
            ssh.close()
        except Exception,ex:
            print Exception,":",ex
        return result

    #文件检测函数
    def file_detect(self, filestr):
        npos = filestr.rfind('/')
        str1 = filestr[0:npos]
        str2 = filestr[npos+1:]
        cmd = 'ls '+ str1
        re = self.ssh_cmd(cmd)
        if str2 in re:
            return True
        else:
            return False

    #服务检测函数
    def service_detect(self, servicestr):
        cmd = 'service '+ servicestr + ' status'
        re = self.ssh_cmd(cmd)
        if 'running' in re:
            return True
        else:
            return False


class NginxServer(LinuxServer):
    '''Monitor linux server and output message
       ssh to other server cmd messge
       check file exist
       check service exist
       check server config file 
    '''
    def __init__(self, server):
        LinuxServer.__init__(self, server)

    #配置文件的配置项检测函数
    def config_detect(self, filestr, key = '', value = ''):
        '''
        需要修改的地儿
        1.同一文件中key跟value必须唯一
        2.key跟value在同一行
        3.没有考虑到key跟value被注释的情况
        4.没有考虑到大小写(例如2m跟2M)
        5.只是简单的值搜索,并不完全匹配,例如某值设置可能为true和untrue,但是在输入为true的情况下两种都会匹配
        
        所以临时解决方案是Config文件
        1.保持key/value唯一
        2.一行式书写

        3.不要注释
        4.大小写严格
        5.如有必要考虑改为正则匹配
        ''' 
        if key == '' and value == '' :
            #仅传文件地址,显示文件全部代码
            cmd = 'cat '+ filestr
            re = self.ssh_cmd(cmd)
            return re
        elif value == '' :
            #仅传文件地址和key,显示key所在行代码
            cmd = 'cat '+ filestr + '| grep ' + key
            re = self.ssh_cmd(cmd)
            return re
        else :
            cmd = 'cat '+ filestr + '| grep ' + key
            re = self.ssh_cmd(cmd)
            if value in re:
                return True
            else :
                return False


class RedisServer(LinuxServer):
    '''Monitor linux server and output message
       ssh to other server cmd messge
       check file exist
       check service exist
       check redis service 
    '''
    def __init__(self, server):
        LinuxServer.__init__(self, server)
        self.redisport = server['redisport']

    def redis_detect(self):
        flag = 0
        try:
            r = redis.Redis(host=self.hostname, port=self.redisport, db=0)
            bAdd = r.set('foo', 'bar') #True
            if bAdd == True:
                flag = flag+1
            bGet = r.get('foo')#bar  
            if bGet == 'bar':
                flag = flag+1
            bDel = r.delete('foo')#1
            if bDel == 1:
                flag = flag+1
            delOk = r.get('foo')#None
            if delOk == None :
                flag = flag+1
                
            if flag == 4:
                return True
            else:
                return False
        except Exception:
            return False
# End Linux System

# Windows System
class LocalHost():
    '''Monitor LocalHost ping status and port status and output message '''
    def __init__(self):
        pass # An empty block

    #检测端口或者地址能否连接,单一参数为ping,两个参数是socket检测
    def connect_detect(self,hostname,sock=0):
        tempfile = 'pingtemp.txt'
        if sock == 0 :
            pingResult = os.system("ping %s >%s " % (hostname,tempfile))
            if os.path.isfile(tempfile):
                os.remove(tempfile)
            if pingResult == 0:
                return True
            else:
                return False
            
        else :
            sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sk.settimeout(1)
            try:
                sk.connect((hostname,sock))
                sk.close()
                return True
            except Exception:
                sk.close()
                return False


class WindowsServer:
    '''Monitor server information and analyze system information on LAN.'''
    def __init__(self, computername, username, uerpassword):
        self.computername = computername
        self.username = username
        self.uerpassword = uerpassword

    def tryconnect(self):
        try :
            self.getservice()
            return True
        except :
            return False

    def getservice(self):
        wbemLocator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        connectServerService = wbemLocator.ConnectServer(self.computername, "root/CIMV2", self.username, self.uerpassword)
        return connectServerService
    
    def server_information(self):
        sql = 'SELECT * FROM Win32_OperatingSystem'
        connectServerService = self.getservice()
        colItems = connectServerService.ExecQuery(sql) 
        serverversion = 'System Version : %s %s' % (colItems[0].Caption.encode("UTF8"), colItems[0].OSArchitecture.encode("UTF8"))
        return serverversion

    def server_process_exist(self, processname):
        sql = "SELECT * FROM Win32_Process Where Name = \"%s\"" % processname
        connectServerService = self.getservice()
        colItems = connectServerService.ExecQuery(sql) 
        if len(colItems) > 0:
            return 1
        else:
            return 0   
    

class ServiceServer(WindowsServer):
    '''Monitor Service Server information and analyze system information on LAN.'''
    def __init__(self, computername, username, uerpassword):
        WindowsServer.__init__(self, computername, username, uerpassword)

    def server_file_exist(self, filename):
        sql = 'SELECT * FROM CIM_Datafile Where Name = "%s"' % filename
        connectServerService = self.getservice()
        colItems = connectServerService.ExecQuery(sql)  
        if len(colItems) > 0:
            return 1
        else:
            return 0

    def server_directory_exist(self, directoryname):
        sql = 'SELECT * FROM Win32_Directory Where Name = "%s"' % directoryname
        connectServerService = self.getservice()
        colItems = connectServerService.ExecQuery(sql) 
        if len(colItems) > 0:
            return 1
        else:
            return 0
        
    def server_mappedlogicaldisk_exist(self, diskname, diskpath):
        sql = 'Select * from Win32_MappedLogicalDisk Where Name = "%s"' % diskname
        connectServerService = self.getservice()
        colItems = connectServerService.ExecQuery(sql)
        if len(colItems) > 0:
            if colItems[0].ProviderName == diskpath:
                return 1
            else:
                return 0
        else:
            return 0
        
    
class IISServer(WindowsServer):
    '''Monitor IIS Server information and analyze system information on LAN.'''
    def __init__(self, computername, username, uerpassword):
        WindowsServer.__init__(self, computername, username, uerpassword)

    def tryconnect(self):
        try :
            self.getservice_()
            return True
        except :
            return False
        
    def getservice_(self):
        wbemLocator = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        wbemLocator.Security_.AuthenticationLevel = 6 #http://msdn.microsoft.com/en-us/library/aa393972(v=vs.85).aspx
        connectServerService = wbemLocator.ConnectServer(self.computername, "root/WebAdministration", self.username, self.uerpassword)
        return connectServerService

    def server_application_exist(self, applicationname):
        sql = 'SELECT * FROM Application Where SiteName = "%s"' % applicationname
        connectServerService = self.getservice_()
        colItems = connectServerService.ExecQuery(sql)
        if len(colItems) > 0 :
            return 1
        else :
            return 0
        
    def server_applicationpool_status(self, applicationpoolname): 
        sql = 'SELECT * FROM ApplicationPool Where Name = "%s"' % applicationpoolname
        connectServerService = self.getservice_()
        colItems = connectServerService.ExecQuery(sql)
        if len(colItems) > 0 :
            if colItems[0].GetState == 1 :
                return 1
            else :
                return 0
        else :
            return -1

    def server_applicationpool_identity(self, applicationpoolname, identityUserName, identityPassword): 
        sql = 'SELECT * FROM ApplicationPool Where Name = "%s\"' % applicationpoolname
        connectServerService = self.getservice_()
        colItems = connectServerService.ExecQuery(sql)
        if len(colItems) > 0 :
            
            if colItems[0].ProcessModel.IdentityType == 3:   #http://msdn.microsoft.com/zh-cn/library/microsoft.web.administration.processmodelidentitytype(v=vs.90).aspx
                
                if colItems[0].ProcessModel.UserName != identityUserName : #http://msdn.microsoft.com/zh-cn/library/microsoft.web.administration.applicationpoolprocessmodel.identitytype(v=vs.90).aspx
                    return 0
                elif colItems[0].ProcessModel.Password != identityPassword :
                    return 0
                else :
                    return 1
            else :
                return -2
        else :
            return -1
# End Windows System





def monitor_nginxserver():
    print 'Start monitor nginxserver'
    messages = []
    for item in MonitorConfig._NginxServerService_:
        linuxserver = LinuxServer(item[0])
        re = linuxserver.service_detect(item[1])
        if re == True:
          output = '[Success] Service %s is running on nginxserver %s.' % (item[1], item[0]['hostname'])
        else:
          output = '[Failed!] Service %s is NOT running on nginxserver %s!' % (item[1], item[0]['hostname'])
        print output
        messages.append(output)
    for item in MonitorConfig._NginxServerFile_:
        linuxserver = LinuxServer(item[0])
        re = linuxserver.file_detect(item[1])
        if re == True:
          output = '[Success] File %s is exist on nginxserver %s.' % (item[1], item[0]['hostname'])
        else:
          output = '[Failed!] File %s is NOT exist on nginxserver %s!' % (item[1], item[0]['hostname'])
        print output
        messages.append(output)
    for item in MonitorConfig._NginxServerConfig_:
        nginxserver = NginxServer(item[0])
        re = nginxserver.config_detect(item[1],item[2],item[3])
        if re == True:
          output = '[Success] Config file "%s" [%s] is [%s] on nginxserver %s.' % (item[1],item[2],item[3],item[0]['hostname'])
        else:
          output = '[Failed!] Config file "%s" [%s] is NOT [%s] on nginxserver %s!' % (item[1],item[2],item[3],item[0]['hostname'])
        print output
        messages.append(output)
    return messages

def monitor_redisserver():
    print 'Start monitor redisserver'
    messages = []
    redisserver = RedisServer(MonitorConfig._Redis_)
    re = redisserver.redis_detect()
    if re == True:
        output = '[Success] Redis CRUD Service is ok on redisserver %s.' % MonitorConfig._Redis_['hostname']
    else:
        output = '[Failed!] Redis CRUD Service is NOT ok on redisserver %s!' % MonitorConfig._Redis_['hostname']
    print output
    messages.append(output)
    return messages

def monitor_localhost():
    print 'Start monitor localhost'
    localhost = LocalHost()
    messages = []
    for item in MonitorConfig._HostNeedToPing_:
        re = localhost.connect_detect(item)
        if re == True:
            output = '[Success] Ping server %s is success.' % item
        else:
            output = '[Failed!] Ping server %s is Failed! ' % item
        print output
        messages.append(output)
    for item in MonitorConfig._PortNeedToDetect_:
        re = localhost.connect_detect(item[0],item[1])
        if re == True:
            output = '[Success] Connect Server port %s:%s is success.' % (item[0], item[1])
        else:
            output = '[Failed!] Connect Server port %s:%s is Failed! ' % (item[0], item[1])
        print output
        messages.append(output)
    return messages

def monitor_serviceserver():
    print 'Start monitor serviceserver'
    _ServiceServerName =  MonitorConfig._ServiceServer_['hostname']
    _ServiceServerUserName = MonitorConfig._ServiceServer_['username']
    _ServiceServerPassword = MonitorConfig._ServiceServer_['password']
    _ServiceServerProgresses = MonitorConfig._ServiceServerProgresses_
    _ServiceServerFiles = MonitorConfig._ServiceServerFiles_
    _ServiceServerDirectorys = MonitorConfig._ServiceServerDirectorys_
    _ServiceServerLogicDisks= MonitorConfig._ServiceServerLogicDisks_

    messages = []

    serviceserver = ServiceServer(_ServiceServerName,_ServiceServerUserName,_ServiceServerPassword)
    connected = serviceserver.tryconnect()
    if connected != True :
        message = '[Failed!] Can not open the client to connect remote server %s! on LAN' % _ServiceServerName
        messages.append(message)
        print message
    else:
        for sprogress in _ServiceServerProgresses:
            exist = serviceserver.server_process_exist(sprogress)
            if exist == 1:
                message = '[Success] The progess %s is exist on ServieServer %s' % (sprogress,_ServiceServerName)
                messages.append(message)
                print message
            else:
                message = '[Failed!] The progess %s is not exist on ServieServer %s' % (sprogress,_ServiceServerName)
                messages.append(message)
                print message
        for sfile in _ServiceServerFiles:
            exist = serviceserver.server_file_exist(sfile)
            if exist == 1:
                message = '[Success] The file %s is exist on ServieServer %s' % (sfile,_ServiceServerName)
                messages.append(message)
                print message
            else:
                message = '[Failed!] The file %s is not exist on ServieServer %s' % (sfile,_ServiceServerName)
                messages.append(message)
                print message
        for sdirectory in _ServiceServerDirectorys:
            exist = serviceserver.server_directory_exist(sdirectory)
            if exist == 1:
                message = '[Success] The directory %s is exist on ServieServer %s' % (sdirectory,_ServiceServerName)
                messages.append(message)
                print message
            else:
                message = '[Failed!] The directory %s is not exist on ServieServer %s' % (sdirectory,_ServiceServerName)
                messages.append(message)
                print message
        for slogicdisk in _ServiceServerDirectorys:
            exist = serviceserver.server_mappedlogicaldisk_exist(slogicdisk[0],slogicdisk[1])
            if exist == 1:
                message = '[Success] The MappedLogicaldDisk %s%s is exist on ServieServer %s' % (slogicdisk[0],slogicdisk[1],_ServiceServerName)
                messages.append(message)
                print message
            else:
                message = '[Failed!] The MappedLogicaldDisk %s%s is not exist on ServieServer %s' % (slogicdisk[0],slogicdisk[1],_ServiceServerName)
                messages.append(message)
                print message
    return messages
      
def monitor_iisserver():
    print 'Start monitor iisserver'
    _IISServerName = MonitorConfig._IISServer_['hostname']
    _IISServerUserName = MonitorConfig._IISServer_['username']
    _IISServerPassword = MonitorConfig._IISServer_['password']
    _IISServerApplications= MonitorConfig._IISServerApplications_
    _IISServerApplicationPools= MonitorConfig._IISServerApplicationPools_

    iismessages = []

    iisserver = IISServer(_IISServerName,_IISServerUserName,_IISServerPassword)
    connected = iisserver.tryconnect()
    if connected != True :
        message = '[Failed!] Can not open the client to connect remote server %s! on LAN' % _IISServerName
        iismessages.append(message)
        print message
    else:
        for iapplication in _IISServerApplications:
            exist = iisserver.server_application_exist(iapplication)
            if exist == 1:
                message = '[Success] The application %s is exist on IISServer %s' % (iapplication,_IISServerName)
                iismessages.append(message)
                print message
            else:
                message = '[Failed!] The application %s is not exist on IISServer %s' % (iapplication,_IISServerName)
                iismessages.append(message)
                print message
        for iapplicationpool in _IISServerApplicationPools:
            identity = iisserver.server_applicationpool_identity(iapplicationpool[0],iapplicationpool[1],iapplicationpool[2])
            if identity == 1:
                message = '[Success] The applicationpool %s identity is correct on IISServer %s' % (iapplicationpool,_IISServerName)
                iismessages.append(message)
                print message
            elif identity == 0:
                message = '[Failed!] The applicationpool %s identity username or password is not correct on IISServer %s' % (iapplicationpool,_IISServerName)
                iismessages.append(message)
                print message
            elif identity == -2:
                message = '[Failed!] The applicationpool %s identity type is not SpecificUser on IISServer %s' % (iapplicationpool[0],_IISServerName)
                iismessages.append(message)
                print message
            else:
                message = '[Failed!] The applicationpool %s is not exist on IISServer %s' % (iapplicationpool[0],_IISServerName)
                iismessages.append(message)
                print message
    return iismessages

def mylogger(messages):
    logfile = 'log.txt'
    logger = logging.getLogger()
    hdlr = logging.FileHandler(logfile)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.info('###############################################################################################')
    for m in messages:
        logger.info(m)
    logger.info('###############################################################################################')
    

if __name__ == '__main__':
    messages_localhost = monitor_localhost()
    messages_nginxserver = monitor_nginxserver()
    messages_redisserver = monitor_redisserver()
    messages_serviceserver = monitor_serviceserver()
    messages_iisserver = monitor_iisserver()
    logmessages = []
    for m in messages_localhost:
        logmessages.append(m)
    for m in messages_nginxserver:
        logmessages.append(m)
    for m in messages_redisserver:
        logmessages.append(m)
    for m in messages_serviceserver:
        logmessages.append(m)
    for m in messages_iisserver:
        logmessages.append(m)
    custom_input= raw_input("Press [Enter] key to create a log file...")
    mylogger(logmessages)




