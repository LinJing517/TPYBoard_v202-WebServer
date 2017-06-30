try:
    import usocket as socket
except:
    import socket
import network
from machine import UART
from machine import Pin

led_flag=Pin(2, Pin.OUT)#esp8266ģ���ϵ�С�� �ߵ�ƽ:�� �͵�ƽ:��
led = Pin(4, Pin.OUT)#��������ܵĿ�������
motor = Pin(5, Pin.OUT)#ֱ������Ŀ�������
#��ʼ��
led.low()
motor.low()
led_flag.high()
def do_connect(ssid,pwd):
    sta_if = network.WLAN(network.STA_IF)#STA ģʽ
    sta_if.active(False)
    if not sta_if.isconnected():#�ж��Ƿ�����
        sta_if.active(True)
        sta_if.connect(ssid,pwd)#ssid:WIFI���� pwd:WIFI ����
        while not sta_if.isconnected():
            pass
    if sta_if.isconnected():
        return sta_if.ifconfig()[0]
def main(ip_,dev_data,login_data,name,pwd):

    s = socket.socket()
    ai = socket.getaddrinfo(ip_, 80)
    addr = ai[0][-1]
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    led_flag.low()
    #s_data=login_data
    while True:
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        led_flag.high()
        req =client_s.readline()
        while True:
            h = client_s.readline()
            if h == b"" or h == b"\r\n":
                break
            #print(h)
            req+=(h.decode('utf-8').lower())
        print("Request:")
        req=req.decode('utf-8').lower().split('\r\n')
        #http header ����
        req_data=req[0].lstrip().rstrip().replace(' ','')
        print(req_data)
        if req_data.find('favicon.ico')>-1:
            client_s.close()
            continue
        else:
            if len(req_data)<=12:
                #˵���ǵ�һ�η��ʣ�����login.html
                s_data=login_data
            else:
                req_data=req_data.replace('get/?','').replace('http/1.1','')
                _name=req_data.find('name')
                _pwd=req_data.find('pwd')
                if _name>-1 and _pwd>-1:
                    #�ж��Ƿ����û���¼
                    if req_data.find(name)>-1 and req_data.find(pwd)>-1:
                        s_data=dev_data
                        print('Login Success!')
                    else:
                        f=open('fail.html','r')
                        s_data=f.read()
                        f.close()
                        print('Login Fail!')
                else:
                    #�ж��Ƿ��ǿ���LED
                    _index=req_data.find('led=')
                    if _index>-1:
                        s_data=dev_data
                        led_val=req_data[_index+4:_index+6].lstrip().rstrip()
                        print('led:',led_val)
                        if led_val=='on':
                            led.value(1)
                        else:
                            led.value(0)
                    #�ж��Ƿ��ǿ��Ƶ��
                    _index=req_data.find('motor=')
                    if _index>-1:
                        s_data=dev_data
                        motor_val=req_data[_index+6:_index+8].lstrip().rstrip()
                        print('motor_val:',motor_val)
                        if motor_val=='on':
                            motor.value(1)
                        else:
                            motor.value(0)
            print('-----------')
            client_s.send(s_data)
            client_s.close()
        led_flag.low()
        
f=open('device.html','r')
dev_html=f.read()
f.close()
f=open('login.html','r')
login_html=f.read()
f.close()
f=open('info.txt','r')
info=f.read()
f.close()
name=info.split(',')[0].lstrip().rstrip()
pwd=info.split(',')[1].lstrip().rstrip()
print('name:',name)
print('pwd:',pwd)
myip_=do_connect('essid','pwd')#���������WIFI���ƺ�����
print(myip_)
main(myip_,dev_html,login_html,name,pwd)