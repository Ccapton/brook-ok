#coding:utf-8
from __future__ import print_function
from __future__ import division
import sys,os
import platform
import ssl

import imp
imp.reload(sys)

brook_pid = ''
ss_pid = ''

brook_version = ''

version = '0.9.5'
title = ' Brook服务端配置程序 v%s '% version
headline = '-'*10 + title +'-'*10

config_json_path = 'brook-ok_config.json'

import random
random_port = random.randint(10000, 30000)
random_port2 = random.randint(10000, 30000)
while random_port == random_port2:
    random_port2 = random.randint(10000, 30000)

default_config_json = {
    'brook':[{'port':random_port,'psw':str(random_port)}],
    'shadowsocks':[{'port':random_port2,'psw':str(random_port2)}]
}

INDEX_BACK = '0'

INDEX_BROOK_ACTION = '1'
INDEX_MANAGE_BROOK = '2'
INDEX_CURRENT_CONFIG = '3'
INDEX_UPGRADE = '4'
INDEX_ABOUT = '5'
INDEX_EXIT = '6'

INDEX_BROOK_ACTION_START = '1'
INDEX_BROOK_ACTION_STOP = '2'
INDEX_BROOK_ACTION_RESTART = '3'
INDEX_SS_ACTION_START = '4'
INDEX_SS_ACTION_STOP = '5'
INDEX_SS_ACTION_RESTART = '6'
INDEX_BROOK_ACTION_UPGRADE = '7'
INDEX_BROOK_ACTION_DELETE = '8'

INDEX_MANAGE_BROOK_ADDBROOK = '1'
INDEX_MANAGE_BROOK_EDITBROOK = '2'
INDEX_MANAGE_BROOK_DELETEBROOK = '3'
INDEX_MANAGE_BROOK_ADDSS = '4'
INDEX_MANAGE_BROOK_EDITSS = '5'
INDEX_MANAGE_BROOK_DELETESS= '6'

INDEX_MANAGE_BROOK_EDIT_PORT = '1'
INDEX_MANAGE_BROOK_EDIT_PSW = '2'

########颜色代码########
RED="31m"      # Error message
GREEN="32m"    # Success message
YELLOW="33m"   # Warning message
PURPLE="35m"     # key message
BLUE="34m"     # Info message

python_version = sys.version
if python_version.startswith('2.'):
    python_version = '2'
elif python_version.startswith('3.'):
    python_version = '3'

def okInput(promt):
    if python_version == '2':
        try:
            return raw_input(promt)
        except KeyboardInterrupt or ValueError:
            print('')
            exit(0)
    else:
        try:
            return input(promt)
        except KeyboardInterrupt or ValueError:
            print('')
            exit(0)

# 指定颜色打印
def colorPrint(color,text):
    print("\033[%s%s\033[0m" % (color,text))

def get_host_ip():
    import socket
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        if s:s.close()
    return ip

def guestPlatform(isUpgrade=False):
    sys_name = platform.system()
    machine_name = platform.machine().lower()
    if 'Darwin' == sys_name:
        isMac(isUpgrade)
    elif 'Linux' == sys_name:
        arch = os.popen('uname -m').read()
        arch = arch[:len(arch) - 1]
        isLinux(isUpgrade,arch)
    elif 'Windows' == sys_name:
        print('暂不支持Windows平台,请期待作者完成')
        #isWindows(isUpgrade,machine_name)
    else:
        print('暂不支持此平台')

def isMac(isUpgrade,):
    brook_list = brookReleaseJson(matchBrookReleaseLinkList())
    for brook in brook_list:
        if 'darwin'in brook['name'] :
            downloadBrook(isUpgrade,brook['url'])
            break

def isLinux(isUpgrade,arch):
    brook_list = brookReleaseJson(matchBrookReleaseLinkList())
    for brook in brook_list:
        if str(brook['name']).endswith('brook') and arch == 'x86_64':
            downloadBrook(isUpgrade,brook['url'])
            break
        elif 'linux' in brook['name']  and arch == 'x86' and '386' in brook['name']:
            downloadBrook(isUpgrade,brook['url'])
            break
        elif 'linux' in brook['name'] and arch in brook['name']:
            downloadBrook(isUpgrade,brook['url'])
            break
        else:
            downloadBrook(isUpgrade,brook_list[0]['url'])
            break

def isWindows(isUpgrade,machine_name):
    brook_list = brookReleaseJson(matchBrookReleaseLinkList())
    for brook in brook_list:
        if str(brook['name']).endswith('amd64.exe') and machine_name == 'amd64':
            downloadBrook(isUpgrade,brook['url'],isExe=True)
            break
        elif str(brook['name']).endswith('386.exe'):
            downloadBrook(isUpgrade,brook['url'],isExe=True)
            break

def getHtmlSource(url):
    html_source = ''
    context = ssl._create_unverified_context()
    if python_version == '3':
        import urllib.request as req
    else:
        import urllib as req
    try:
        try:
            f = req.urlopen(url, context=context)
            html_source = f.read()
            f.close()
        except KeyboardInterrupt:
            print('\n取消请求')
    except Exception:
        print('请求错误，请重试')
    return html_source

def downloadBrook(isUpgrade,url,isExe=False):
    if isUpgrade:
        stopBrook()

    print(' 开始下载brook ' + url)
    command = 'curl -o brook_temp -L ' + url
    code = os.system(command)
    if code != 0:
        print('')
        colorPrint(RED,' 下载brook错误，请重新运行本程序')
        os.system('rm -rf brook_temp')
        return
    brookname = 'brook'
    if not isExe:
        command2 = 'rm -rf brook && mv brook_temp brook'
        os.system(command2)
        command3 = 'chmod +x brook'
        os.system(command3)
    else:
        brookname = 'brook.exe'
        os.remove(os.path.join(sys.path[0], brookname))
        os.rename(os.path.join(sys.path[0], 'brook_temp'), os.path.join(sys.path[0], brookname))
    colorPrint(PURPLE, " brook下载完毕!保存在："+os.path.join(sys.path[0],brookname))

def showState():
    print('当前服务状态：')
    if hasBrookStart() and hasShadowsocksStart():
        colorPrint(GREEN, ' Brook、ShadowSocks运行中')
    elif hasBrookStart() and not hasShadowsocksStart():
        colorPrint(YELLOW,' Brook运行中')
    elif hasShadowsocksStart() and not hasBrookStart():
        colorPrint(YELLOW,' ShadowSocks运行中')
    else:
        colorPrint(RED,'服务未运行')

def MainMenu(clear=True):
    printProgramInfo(clear)
    printVersionInfo()
    showState()
    colorPrint(BLUE, '-' * 30)
    print('')
    colorPrint(PURPLE, ' 1、管理服务')
    colorPrint(PURPLE, ' 2、配置节点')
    colorPrint(PURPLE, ' 3、显示节点')
    print('')
    colorPrint(PURPLE, ' 4、升级')
    colorPrint(PURPLE, ' 5、关于')
    colorPrint(PURPLE, ' 6、退出')
    print('')
    colorPrint(BLUE, '-' * 30)
    optionIndex = INDEX_BACK
    optionIndex = okInput('输入对应数字（ctrl+c退出）：')
    if  optionIndex == INDEX_BROOK_ACTION:
        brookAction()
    elif optionIndex == INDEX_MANAGE_BROOK:
        manageBrook()
    elif optionIndex == INDEX_CURRENT_CONFIG:
        showCurrentConfig()
    elif optionIndex == INDEX_UPGRADE:
        upgrade()
    elif optionIndex == INDEX_EXIT:
        exit(0)
    elif optionIndex == INDEX_ABOUT:
        os.system('clear')
        aboutBrook()
    else:
        MainMenu()

def loadConfigJson():
    import json
    if not os.path.exists(config_json_path):
        os.system("touch %s" % config_json_path)
    f = open(config_json_path,'r')
    jsonstr = f.read()
    f.close()
    if jsonstr == '':
        with open(config_json_path, 'w') as f2:
            f2.write(json.dumps(default_config_json,ensure_ascii=False))
    f = open(config_json_path,'r')
    jsonstr = f.read()
    configjson = json.loads(jsonstr)
    f.close()
    return configjson

def saveConfigJson(configjson):
    import json
    with open(config_json_path,'w') as f:
        f.write(json.dumps(configjson,ensure_ascii=False))


def showCurrentConfig(justShow=False,showBrook=True,showSS=True):
    print('')
    print('当前配置:')
    print('')
    configjson = loadConfigJson()
    host_ip = get_host_ip()
    if showBrook:
        brook_list = configjson['brook']
        print(' 服务类型(B)：Brook')
        for index in range(len(brook_list)):
            brook = brook_list[index]
            print(" (%d)" % (index + 1))
            colorPrint(GREEN, "----地址：" + host_ip)
            colorPrint(GREEN, "----端口：" + str(brook['port']))
            colorPrint(GREEN, "----密码：" + str(brook['psw']))
        print('')
    if showSS:
        ss_list = configjson['shadowsocks']
        print(' 服务类型(S)：ShadowSocks')
        for index in range(len(ss_list)):
            ss = ss_list[index]
            print(" (%d)" % (index + 1))
            colorPrint(GREEN, "----地址：" + host_ip)
            colorPrint(GREEN, "----端口：" + str(ss['port']))
            colorPrint(GREEN, "----密码：" + str(ss['psw']))
            colorPrint(GREEN, "----加密协议：aes-256-cfb")
        print('')
    optionIndex = INDEX_BACK
    if not justShow:
        optionIndex = okInput('输入数字0返回上级 (其他字符退出）：')
        if optionIndex == INDEX_BACK:
            MainMenu()
        else:
            exit(0)

def manageBrook():
    colorPrint(BLUE, '-' * 30)
    print('')
    colorPrint(PURPLE, ' 1、添加Brook节点')
    colorPrint(PURPLE, ' 2、修改Brook节点')
    colorPrint(PURPLE, ' 3、删除Brook节点')
    print('')
    colorPrint(PURPLE, ' 4、添加ShadowSocks节点')
    colorPrint(PURPLE, ' 5、修改ShadowSocks节点')
    colorPrint(PURPLE, ' 6、删除ShadowSocks节点')
    print('')
    colorPrint(BLUE, '-' * 30)
    optionIndex = INDEX_BACK
    optionIndex = okInput('输入数字0返回上级 (其他字符退出）：')
    if optionIndex == INDEX_MANAGE_BROOK_ADDBROOK:
        addPort(isBrook=True)
    elif optionIndex == INDEX_MANAGE_BROOK_EDITBROOK:
        editPort(isBrook=True)
    elif optionIndex == INDEX_MANAGE_BROOK_DELETEBROOK:
        delPort(isBrook=True)
    elif optionIndex == INDEX_MANAGE_BROOK_ADDSS:
        addPort(isBrook=False)
    elif optionIndex == INDEX_MANAGE_BROOK_EDITSS:
        editPort(isBrook=False)
    elif optionIndex == INDEX_MANAGE_BROOK_DELETESS:
        delPort(isBrook=False)
    elif optionIndex == INDEX_BACK:
        MainMenu()
    else:
        exit(0)


def addPort(isBrook=True):
    configjson = loadConfigJson()
    import random
    randomport = random.randint(10000, 30000)
    port = okInput('输入一个端口号(回车使用随机端口：%d):' % randomport)
    if port == '':
        port = randomport
    try:
        port = int(port)
    except:
        colorPrint(RED, '端口号必须为大于1023的数字')
        manageBrook()
    if port <= 1023:
        colorPrint(RED, '端口号必须为大于1023的数字')
        manageBrook()
    if isPortUsed(port, configjson):
        colorPrint(RED, '端口 ' + str(port) + ' 已被占用了')
        manageBrook()
    else:
        randompsw = random.randint(10000, 30000)
        psw = okInput('输入密码(回车使用随机密码：%d):' % randompsw)
        if psw == '':
            psw = randompsw
        if isBrook:
            configjson['brook'].append({'port':port,'psw':str(psw)})
        else:
            configjson['shadowsocks'].append({'port':port,'psw':str(psw)})
        saveConfigJson(configjson)
        restartBrook()
        manageBrook()

def editPort(isBrook=True):
    configjson = loadConfigJson()
    showCurrentConfig(justShow=True, showBrook=isBrook, showSS=(not isBrook))
    if isBrook:
        length = len(configjson['brook'])
    else:
        length = len(configjson['shadowsocks'])
    if length == 0:
        colorPrint(RED, '当前服务没有节点，请添加一个节点端口吧')
        manageBrook()
    index = okInput('输入你想要修改的节点序号:')
    try:
        index = int(index)
        if index > length or index <= 0:
            colorPrint(RED, '节点的序号不在范围内，请查看配置信息进行操作')
            editPort(isBrook)
    except:
        colorPrint(RED, '节点的序号必须为大于0的数字，请查看配置信息进行操作')
        editPort(isBrook)
    index -= 1
    if isBrook:
        currentService = configjson['brook'][index]
    else:
        currentService = configjson['shadowsocks'][index]
    colorPrint(BLUE, '-' * 30)
    if isBrook:print('修改Brook端口')
    else:print('修改ShadowSocks端口')
    print('')
    colorPrint(PURPLE, " 1、修改端口号 (当前"+str(currentService['port'])+")")
    colorPrint(PURPLE, " 2、修改密码   (当前"+str(currentService['psw'])+")")
    print('')
    colorPrint(BLUE, '-' * 30)
    optionIndex = okInput('选择修改一项 (其他字符退出）：')
    if optionIndex == INDEX_MANAGE_BROOK_EDIT_PORT:
        import random
        randomport = random.randint(10000, 30000)
        newport = okInput('输入一个新的端口号(回车使用随机端口：%d):' % randomport)
        if newport == '':
            newport = randomport
        try:
            newport = int(newport)
        except:
            colorPrint(RED, '端口号必须为大于1023的数字')
            editPort(isBrook)
        if newport <= 1023:
            colorPrint(RED, '端口号必须为大于1023的数字')
            editPort(isBrook)
        if isPortUsed(newport, configjson):
            colorPrint(RED, '端口 ' + str(newport) + ' 已被占用了')
            editPort(isBrook)
        else:
            newpsw = okInput('输入新密码（回车使用原密码 %s）' % str(currentService['psw']))
            if newpsw == '':
                newpsw = currentService['psw']
            currentService['psw'] = newpsw
            currentService['port'] = newport
            colorPrint(YELLOW,'修改中...')
            saveConfigJson(configjson)
            colorPrint(GREEN,'修改成功')
            restartBrook()
    elif optionIndex == INDEX_MANAGE_BROOK_EDIT_PSW:
        newpsw = okInput('输入新密码（回车使用原密码 %s）' % str(currentService['psw']))
        if newpsw == '':
            newpsw = currentService['psw']
        currentService['psw'] = newpsw
        colorPrint(YELLOW, '修改中...')
        saveConfigJson(configjson)
        colorPrint(GREEN, '修改成功')
        if isBrook:restartBrook()
        else:restartShadowsocks()
    else:
        editPort(isBrook)

def delPort(isBrook=True):
    configjson = loadConfigJson()
    showCurrentConfig(justShow=True,showBrook=isBrook,showSS=(not isBrook))
    if isBrook:
        length = len(configjson['brook'])
    else:
        length = len(configjson['shadowsocks'])
    if length == 0:
        colorPrint(RED, '当前服务没有节点，请添加一个节点端口吧')
        manageBrook()
    index = okInput('输入你想要删除的节点序号:')
    try:
        index = int(index)
        if index > length or index <= 0:
            colorPrint(RED, '节点的序号不在范围内，请查看配置信息进行操作')
            manageBrook()
    except:
        colorPrint(RED, '节点的序号必须为大于0的数字，请查看配置信息进行操作')
        manageBrook()
    index -= 1
    try:
        if isBrook:
            configjson['brook'].remove(configjson['brook'][index])
            saveConfigJson(configjson)
            restartBrook()
        else:
            configjson['shadowsocks'].remove(configjson['shadowsocks'][index])
            saveConfigJson(configjson)
            restartShadowsocks()
    except IndexError:
        pass
    manageBrook()


def isPortUsed(port,configjson):
    if port > 0:
        brook_list = configjson['brook']
        ss_list = configjson['shadowsocks']
        for brook in brook_list:
            if port == brook['port']:
                return True
        for ss in ss_list:
            if port == ss['port']:
                return True
        res = os.popen('lsof -i:'+str(port)).read()
        if res != '':
            return True
    return False



def brookAction():
    if not checkBrookExisted():
        MainMenu()
        return
    colorPrint(BLUE, '-' * 30)
    print('')
    colorPrint(PURPLE, ' 1、开启brook')
    colorPrint(PURPLE, ' 2、停止brook')
    colorPrint(PURPLE, ' 3、重启brook')
    print('')
    colorPrint(PURPLE, ' 4、开启shadowsocks')
    colorPrint(PURPLE, ' 5、停止shadowsocks')
    colorPrint(PURPLE, ' 6、重启shadowsocks')
    print('')
    colorPrint(PURPLE, ' 7、升级brook')
    colorPrint(PURPLE, ' 8、删除brook')
    print('')
    colorPrint(BLUE, '-' * 30)
    optionIndex = okInput('输入数字0返回上级 (其他字符退出）：')
    if optionIndex == INDEX_BROOK_ACTION_START:
        print(' 开启brook服务...')
        startBrook(False)
        printProgramInfo()
        MainMenu()
    elif optionIndex == INDEX_BROOK_ACTION_STOP:
        print(' 停止brook服务...')
        stopBrook()
        colorPrint(GREEN, ' 已停止brook服务!')
        MainMenu(clear=False)
    elif optionIndex == INDEX_BROOK_ACTION_RESTART:
        print(' 重启brook服务...')
        restartBrook()
    elif optionIndex == INDEX_SS_ACTION_START:
        print('开启shadowsocks服务...')
        startShadowsocks(False)
        MainMenu()
    elif optionIndex == INDEX_SS_ACTION_STOP:
        print(' 停止shadowsock服务...')
        stopShadowsocks()
        colorPrint(GREEN, ' 已停止shadowsock服务!')
        MainMenu(clear=False)
    elif optionIndex == INDEX_SS_ACTION_RESTART:
        print(' 重启shadowsock服务...')
        restartShadowsocks()
    elif optionIndex == INDEX_BROOK_ACTION_UPGRADE:
        upgradeBrook()
    elif optionIndex == INDEX_BROOK_ACTION_DELETE:
        print(' 删除brook程序...')
        confirm = okInput(' 确定要删除brook吗？(y/n)：')
        if confirm.lower() == 'y':
            stopService(isBrook=True)
            stopService(isBrook=False)
            os.system('rm -rf brook')
            colorPrint(GREEN,' 删除brook成功！')
        MainMenu(clear=False)
    elif optionIndex == INDEX_BACK:
        MainMenu()

def checkBrookExisted():
    if not os.path.exists('brook'):
        confirm = okInput('brook软件不存在,现在下载？(y/n):')
        if confirm.lower() == 'y' or confirm.lower() == 'yes':
            guestPlatform()
            if os.path.exists('brook'):
                return True
        return False
    else:
        return True

def startBrook(stateMode):
    return startService(stateMode,isBrook=True)

def startShadowsocks(stateMode):
    return startService(stateMode,isBrook=False)

def stopBrook():
    hasBrookStart()
    stopService(isBrook=True)

def stopShadowsocks():
    hasShadowsocksStart()
    stopService(isBrook=False)

def restartBrook(stateMode=False):
    stopBrook()
    startBrook(stateMode)

def restartShadowsocks(stateMode=False):
    stopShadowsocks()
    startShadowsocks(stateMode)

def hasBrookStart():
    return hasServiceStart(isBrook=True)

def hasShadowsocksStart():
    return hasServiceStart(isBrook=False)

def startService(stateMode,isBrook=True):
    if isBrook:
        service_name = 'brook'
    else:
        service_name = 'shadowsocks'
    if isBrook:server_list = loadConfigJson()['brook']
    else:server_list = loadConfigJson()['shadowsocks']
    server_list_str = ''
    for server in server_list:
        server_str = '-l ":%d %s" ' % (server['port'], server['psw'])
        server_list_str += server_str
    if not stateMode:
        if hasServiceStart(isBrook):
            colorPrint(YELLOW, ' %s服务已经开启，不要重复操作' % service_name)
            showCurrentConfig(showBrook=isBrook,showSS=(not isBrook))
            return 0
        else:
            code1 = -2
            if len(server_list_str) != 0:
                if isBrook:
                    code1 = os.system('nohup ./brook servers ' + server_list_str + '--tcpDeadline 10 >/dev/null 2>log &')
                else:
                    code1 = os.system('nohup ./brook ssservers ' + server_list_str + '--tcpDeadline 10 >/dev/null 2>log &')
            if code1 == 0:
                # 这时 brook_pid,ss_pid 未被记录
                hasServiceStart(isBrook)  # 为了记录brook_pid,ss_pid
                colorPrint(GREEN, '%s服务开启成功！' % service_name)
                showCurrentConfig(showBrook=isBrook, showSS=(not isBrook))
                return 0
            else:
                hasBrookStart()
                hasServiceStart(isBrook)
                if code1 != 0:
                    colorPrint(RED, ' %s服务开启失败' % service_name)
                else:
                    colorPrint(GREEN, ' %s服务开启成功' % service_name)
                if code1 == -2:
                    colorPrint(RED, ' %s节点为空，请添加一些节点' % service_name)
    else:
        if hasServiceStart(isBrook) :
            return 1
        else:
            return 0
    return 1

def stopService(isBrook=True):
    hasServiceStart(isBrook)
    try:
        global brook_pid,ss_pid
        if isBrook:
            if brook_pid != '':
                os.system('kill ' + brook_pid)
        else:
            if ss_pid != '':
                os.system('kill ' + ss_pid)
    finally:
        pass

def hasServiceStart(isBrook=True):
    result = os.popen('ps aux | grep brook').read()
    try:
        global brook_pid,ss_pid
        if isBrook:brook_pid = matchPid(result, isBrook)
        else:ss_pid = matchPid(result, isBrook)
    except Exception:
        if isBrook:brook_pid = ''
        else:ss_pid = ''
    started = False
    if isBrook:
        if str(result).find(' servers -l') != -1:
            started = True
    else:
        if str(result).find(' ssservers -l') != -1:
            started = True
    return started

def matchPid(text,isBrook=False):
    import re
    if isBrook:
        reresult = re.search('.+\s{1}servers -l.+', str(text))
    else:
        reresult = re.search('.+\s{1}ssservers -l.+', str(text))
    targetline = reresult.group()
    reresult2 = re.search("\S+\s+[\d]+[\s]{0,1}[\d]+\s+\d\.\d", targetline)
    targetline2 = reresult2.group()
    finalresult = re.search("[\d]+[\s]{0,1}[\d]+", targetline2)
    return finalresult.group()

def printProgramInfo(clear=True):
    if clear:
        os.system('clear')
    colorPrint(color=BLUE,text=headline)

def printVersionInfo():
    if not os.path.exists('brook'):return
    print('当前Brook版本:')
    version = os.popen('./brook -version').read()
    colorPrint(GREEN, ' '+str(version).rstrip())
    global brook_version
    brook_version = str(version).rstrip().split(' ')[2]

def getCurrentBrookversion():
    version = os.popen('./brook -version').read()
    current_version = str(version).rstrip().split(' ')[2]
    return current_version

def upgradeBrook():
    global brook_version
    if brook_version == '':
        brook_version = getCurrentBrookversion()
    print('当前brook版本 v'+brook_version)
    print('获取最新brook版本中...')
    latest_version = getBrookLatestVersion()
    if brook_version != '' and (brook_version in latest_version):
        colorPrint(YELLOW,'brook已是最新版本')
        brookAction()
    elif brook_version !='' and (brook_version not in latest_version):
        colorPrint(YELLOW,'有brook新版本'+latest_version)
        confirm = okInput('确定升级（y/n）:')
        if confirm.lower() == 'y' or confirm.lower() == 'yes' or confirm.lower() == 'ye':
            stopBrook()
            stopShadowsocks()
            print('brook升级中...')
            guestPlatform(isUpgrade=True)
        else:
            brookAction()

def downloadLatestVersion(url):
    if os.system('curl -o brook-ok_temp.py -L %s' % url) == 0:
        if os.system('rm -rf brook-ok.py') == 0:
            if os.system('mv brook-ok_temp.py brook-ok.py') == 0:
                colorPrint(GREEN, '更新成功！')
                rest_time = 3
                colorPrint(YELLOW, '%ds后自动重启brook-ok.py' % rest_time)
                import time
                time.sleep(rest_time)
                if os.system('python brook-ok.py') == 0:
                    return
    colorPrint(RED, '更新出错,请重试')


def matchLatestUrl(html_source):
    try:
        import re
        if python_version == '2':
            source = html_source
        else:
            source = html_source.decode(encoding='utf-8')
        result = re.search('https://github.com/Ccapton/brook-ok/releases/download/.+/brook-ok\.py', source).group()
    except Exception:
        result = ''
    return result

def getLatestVersion():
    import re
    url = 'https://raw.githubusercontent.com/Ccapton/brook-ok/master/README.md'
    if python_version == '2':
        source = getHtmlSource(url)
    else:
        source = getHtmlSource(url).decode(encoding='utf-8')
    version_str = re.search('#+\s{1,}\[v\S+\]', source).group()
    version = re.search("[\d\.]+", version_str).group()
    return version

def getBrookLatestVersion():
    import re
    url = 'https://raw.githubusercontent.com/txthinking/brook/master/README.md'
    if python_version == '2':
        source = getHtmlSource(url)
    else:
        source = getHtmlSource(url).decode(encoding='utf-8')
    version_str = re.search('#+\s{1,}.{0,}v\d+',source).group()
    version_num = re.search('20\d+',version_str).group()
    return version_num

# 获取brook其github主页的所有release下载链接
def matchBrookReleaseLinkList():
    url = 'https://github.com/txthinking/brook'
    if python_version == '2':
        source = getHtmlSource(url)
    else:
        source = getHtmlSource(url).decode(encoding='utf-8')
    import re
    result = re.findall('https://github.com/txthinking/brook/releases/download/.+"',source)
    link_list = []
    for raw_link in result:
        link = raw_link[:len(raw_link) - 1]
        link_list.append(link)
    return link_list

def brookReleaseJson(releaseLinkList):
    brookRelease_list = []
    import os
    for link in releaseLinkList:
        released = {}
        released['url']=link
        released['name']=os.path.basename(link)
        brookRelease_list.append(released)
    return brookRelease_list

def upgrade():
    print(' 当前程序版本 v'+version)
    print(' 获取最新版本中...')

    url = 'https://raw.githubusercontent.com/Ccapton/brook-ok/master/README.md'

    latest_version = getLatestVersion()

    if version in latest_version:
        colorPrint(YELLOW,'当前版本 v%s 已是最新版本！' % version)
        MainMenu(clear=False)
    else:
        latest_url = ''
        try:
            latest_url = matchLatestUrl(getHtmlSource(url))
            if latest_url != '':
                colorPrint(YELLOW, '有新版本 ' + latest_version)
                confirm = okInput('确定升级brook-ok（y/n）:')
                if confirm.lower() == 'y' or confirm.lower() == 'yes' or confirm.lower() == 'ye':
                    print('brook-ok升级中...')
                    downloadLatestVersion(latest_url)
                else:
                    MainMenu()
            else:
                colorPrint(YELLOW, '当前版本 v%s 已是最新版本！' % version)
                MainMenu(clear=False)
        except KeyboardInterrupt:
            print('')
            MainMenu()
        except Exception:
            colorPrint(RED,'连接失败，请重试')
            MainMenu()


def aboutBrook():
    brook_url = 'https://github.com/txthinking/brook'
    brook_ok_url = 'https://github.com/ccapton/brook-ok'
    about = '\n    brook是一个跨平台(Linux/MacOS/Windows/Android/iOS)代理 / Vpn软件' \
            '\n一个墙外的服务器利用Brook程序开启brook或shadowsocks服务，墙内的主机利用brook程序开启客户端连接到brook服务器，' \
            '利用加密的数据，达到科学上网的目的。 \n'
    about2 = '\n   brook-ok 为了方便管理、开启brook和shadowsocks服务而生 !>_<! '
    colorPrint(BLUE, '-' * 30)
    print('')
    colorPrint(YELLOW,'----关于brook ')
    print(about)
    print('\nbrook项目地址：'+brook_url+'\n')
    colorPrint(YELLOW,'----关于brook-ok ')
    print(about2)
    print('\nbrook-ok项目地址：'+brook_ok_url+'\n')
    colorPrint(BLUE, '-' * 30)
    okInput('回车返回上级：')
    printProgramInfo()
    printVersionInfo()
    MainMenu()

def Entry():
    MainMenu()

if __name__ == "__main__":
    Entry()
