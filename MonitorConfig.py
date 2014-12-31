_Nginx_ = {
  'hostname':'192.168.3.163', 
  'username':'root', 
  'password':'Password01!',
  'sshport':22
}
_Redis_ = {
  'hostname':'192.168.3.160', 
  'username':'root', 
  'password':'Password01!',
  'sshport':22,
  'redisport':6379,
}

# ping server list
_HostNeedToPing_ = [
  _Nginx_['hostname']
]
# check server port list
_PortNeedToDetect_ = [
  [_Redis_['hostname'],6379],
  [_Nginx_['hostname'],1024]
]
# check server service list
_NginxServerService_ = [
  [_Nginx_,'nginx']
]
# check server file list
_NginxServerFile_ = [
  [_Nginx_,'/etc/nginx/nginx.conf'],
  [_Nginx_,'/mnt/nfs/crossdomain.xml'],
  [_Nginx_,'/mnt/nfs/upload'],
  [_Nginx_,'/mnt/nfs/upload/img/ppt_ico1.png'],
  [_Nginx_,'/mnt/nfs/upload/img/video_pending_ico.png']
]
# check server config file configeration list
_NginxServerConfig_ = [
  [_Nginx_,'/etc/nginx/nginx.conf','sendfile','on'],
  [_Nginx_,'/etc/nginx/nginx.conf','sendfile','off'],
  [_Nginx_,'/etc/nginx/nginx.conf','pid','/var/run/nginx.pid'],
  [_Nginx_,'/etc/nginx/nginx.conf','listen','192.168.3.163'],
  [_Nginx_,'/etc/nginx/nginx.conf','listen','192.168.3.162']
]

_ServiceServer_ = {
    'hostname':'192.168.3.165',
    'username':'administrator',
    'password':'Password01!'
}

_IISServer_ = {
    'hostname':'192.168.3.159',
    'username':'administrator',
    'password':'Password01!'
}

_ServiceServerProgresses_ = [
    'CollegeCourse.Tools.exe',
    'soffice.bin',
    'soffice.exe'
]

_ServiceServerFiles_ = [
    'C:\\\\tools\\\\ffmpeg.exe',
    'C:\\\\tools\\\\pdf2swf.exe',
    'C:\\\\tools\\\\src2pdf.exe',
    'C:\\\\tools\\\\src2pdfJacob.exe',
    'C:\\\\tools\\\\OpenOffice\\\\program\\\\soffice.exe'
]

_ServiceServerDirectorys_ = [
    'C:\\\\Temp'
]
    
_ServiceServerLogicDisks_ = [
    ['Z:','\\\\192.168.3.162\\nas1']
]

_IISServerApplications_ = [
    'CCM'
]
_IISServerApplicationPools_ = [
    ['CCM','root','Password01!']
]
