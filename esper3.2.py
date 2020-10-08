#!/bin/python3.6
#this version should be able to send custom charactes to the ESP
#==============IMPORTS==================

from tkinter import *
import socket, sys, os, time, psutil, subprocess, math, serial


#==============CONSTANTS================
root = Tk()
root.overrideredirect(True)
root.withdraw()
root.deiconify()

#ser = serial.Serial(port='/dev/ttyUSB0', baudrate='s115200', timeout=0)
#root.title("ESPER-GUI")
send = True
host = '192.168.1.109'#192.168.1.109wd
port = 8888
mode = IntVar()

mode.set(1)
delay = 250 # I guess this is optimal, given that i have to refresh the page every time
cur = 0
preva = "                "
prevb = "                "
prevc = "                "
prevclip = ""
lilcounter = 0
backlight = True
prevmode = 0
menu = False
angle = 0
names=[]
step = 10
p = 25 
charh = 8
charw = 5
lines = 1
cols = 1

imgw = cols*charw
imgh = lines*charh

#==============FUNCTIONS================
def modeInfo():
    setCursor(0,0)
    fontSize(2)
    writeChars("ESPER v3.2")
    setCursor(0, 20)
    writeChars("Connected")

    
def modeClock():
    global lilcounter
    global preva
    global prevb
    global delay
    delay = 250
    fontSize(2)
    a = time.strftime("%H:%M:%S", time.localtime())
    b = time.strftime("%d.%m.%y", time.localtime())
    if not a[-2:]==preva[-2:]:
        makeRect(70,0,30,20,3)
        setCursor(70,0)
        writeChars(a[-2:])
    if not a[:-3]==preva[:-3]:
        makeRect(0,0,60,20,3)
        setCursor(0,0)
        writeChars(a[:-2])
    if not b == prevb:
        makeRect(0,25,128,45,3)
        setCursor(0,25)
        writeChars(b)
    preva = a
    prevb = b
    wheelCounter(90,50,12,angle)
#    sendData(15, 0, bytearray(wheelCounter(lilcounter%4))[0])
#    sendData(0, 0, bytearray(wheelCounterReverse(lilcounter%4))[0])


def modeOverview():
    global lilcounter
    global delay
    global preva
    global prevb
    global prevc
    delay = 1000
    if os.name == 'posix':
        lstates = str(subprocess.check_output('xset q', shell=True)[111:175])
        if lstates[16] == "n":
            caps = "A"
        else:
            caps = "a"
        if lstates[40] == "n":
            num = "N"
        else:
            num = "n"
#        if lstates[64] == "n":
#            scrol = "S"
#        else:
#            scrol = "s"
        temp = str(int(psutil.sensors_temperatures()["coretemp"][1].current))
    else:
        caps = "?"
        num = "?"
        temp = "??"

    try:
        bat = str(int(round(psutil.sensors_battery().percent, 0)))
    except AttributeError:
        bat = "xx"
    disk = str(int(psutil.disk_usage('/').percent))
    cpu = str(int(psutil.cpu_percent()))
    ram = str(int(psutil.virtual_memory()[2]))
    swap = str(int(psutil.swap_memory().percent))
    
    a = "C" + cpu + " T" + temp+" "+ num 
    b ="R" +  ram + " B" + bat +" "+caps
    c = "S"+ swap + " D"+ disk+" "+str(lilcounter%4)
    fontSize(2)
    
    if not a == preva:
        setCursor(0,0)
        makeRect(0,0,128,20,3)
        writeChars(a)
    
    if not b == prevb:
        makeRect(0,22,128,20,3)
        setCursor(0,22)
        writeChars(b)
    
    if not c == prevc:
        setCursor(0, 44)
        makeRect(0,44,128,20,3)
        writeChars(c)
    display() 
    preva = a
    prevb =b
    prevc = c
def modeClipboard():
    global prevclip
    clip = root.clipboard_get()
    if not clip == prevclip:
        clearScreen()
        print(clip)
        setCursor(0,0)
        fontSize(1)
        writeChars(clip)
        prevclip = clip

def dialogClose(event):
    global dialog
    dialog.destroy()
    
    
def dialogBox():
    global dialog
    dialog = Toplevel(root)
    dialog.title("Enter time in seconds")
    field = Entry(dialog, textvariable=inp)
    field.pack(side=LEFT) 
    field.delete(0, END)
    field.focus()
    field.bind('<Return>', dialogClose)
    Button(dialog, text="Set", command=dialog.destroy).pack(side=LEFT)
    root.wait_window(dialog)



def modeTimer():
    global cur
    global inp
    

    
    if cur == 0:
        dialogBox()
    try:
        total = int(inp.get())*1000/delay
    except ValueError:
        cur = 0
        mode.set(2)
        return
    makeRect(0,0,128,24, 3)
    setCursor(50,10)
    writeChars(str(int(100*cur/total))+"%")
    progressBar(cur, total)
    cur += 1
    if cur > total:
        cur = 0
        mode.set(2)


def modeCheck():
    global mode
    global lilcounter
    global s
    global prevmode
    global angle
    #clearScreen()
#    setCursor(0, 8)
#    clearScreen()

    
            
    
    display()
    if not mode.get() == prevmode:
        clearScreen()
        global preva
        preva = ""
    if mode.get() == 0: #Display version message
        
        modeInfo()
        
    elif mode.get() == 1: # Simple clock and date
        modeClock()
        
    elif mode.get() == 2: #This is an overview of computer's satus like RAM CPU (also time+date)
        modeOverview()
        
    elif mode.get() == 3:#display clipboard content
        modeClipboard()
        
    elif mode.get() == 4: #timer, counts down 60 seconds
        fontSize(2)
        modeTimer()        
    lilcounter += 1
    prevmode = mode.get()
    sendData(b'\x07')

    if s.recv(1).strip() == b'1':
        mode.set(mode.get()+1)
        if mode.get() >3:
            mode.set(0)
        root.after(1000, modeCheck)




def progressBar(cur, total):
    makeRect(2, 28, 126,8, 1)
    leng = cur/total*124 
    makeRect(2,28,int(2+leng), 8, 4)
    display()
        
    
def wheelCounter(x, y, r, angle):
    
    makeCircle(x,y,r,1)
    makeCircle(x,y,r-1,3)
    makeLine(x,y,int(x-(math.cos(math.radians(angle))*r)),int(y-(math.sin(math.radians(angle))*r)),1)



def wheelCounterReverse(val):
    if val == 0:
        return b"|"
    elif val == 1:
        return b"\x00"
    elif val == 2:
        return b"-"
    elif val == 3:
        return b"/"


def openSocket():
    global send
    print("Socket creation")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return s
    except socket.error: 
        send = False
        print("Couldn't create a socket. Retrying in 5s.")
        root.after(5000, openSocket)


def resolveHostname():
    global send
    global host
    global port
    
    print("Resolving host IP")
    try:
            ip = socket.gethostbyname(host)
            return ip
    except socket.gaierror:
        print("Hostname wasn't resolved. Retrying in 5s")
        root.after(5000, resolveHostname)
    
    

def establishConnection():
    global s
    global port
    s = openSocket()
    ip = resolveHostname()    

    print("Connecting to "+ str(ip) + " on port " + str(port))
    s.connect((ip, port))
    print("Connection succesful!")
    
         
def toggleSend():
    global send
    global s
    send = not send
    if send:
        b1.config(relief="sunken", text="1")
        s.send(bytes(b'\x08'))
    else:
        b1.config(relief="raised", text="0")
        s.send(bytes(b'\x09'))

def toggleMenu():

    global menu
    menu = not menu
    if menu:
        bv.config(relief="sunken", text="<")
        frame2.pack(side=LEFT)
        
    elif not menu:
        bv.config(relief="raised", text=">")
        frame2.pack_forget()


def toggleBacklight():
    global backlight
    backlight = not backlight
    if backlight:
        bl.config(relief="sunken", text="BL")
        
    elif not backlight:
        bl.config(relief="raised", text="Bl")
    #print(send)
    sendData(15, 0, bytearray(" ".encode())[0])
    global preva
    preva = preva[:15] + " " 
def makeRect(x, y, w, h, color):
    global s #color: {0 black 1 white 2 inverse}(empty){3 black 4 white 5 inverse}(filled)
    msg = [20,x,y,w,h,color]
    msg = bytes(msg)
    print(msg)
    s.send(msg)
def makeCircle(x, y,r, color):
    global s #color: {0 black 1 white 2 inverse}(empty){3 black 4 white 5 inverse}(filled)
    msg = [21,x,y,r,color]
    msg = bytes(msg)
    
    print(msg)
    s.send(msg)
def makeLine(x, y, w, h, color):
    global s #color: {0 black 1 white 2 inverse}(empty)
    msg = [22,x,y,w,h,color]
    msg = bytes(msg)
    print(msg)
    s.send(msg)
def makeTriangle(x, y, w, h, p, q, color):
    global s #color: {0 black 1 white 2 inverse}(empty)
    msg = [23,x,y,w,h,color]

    msg = bytes(msg)
    print(msg)
    s.send(msg)

def writeChars(string):
    global s
    s.send(bytes(b'\x0A'))
    
    for i in string:
        s.send(bytes(i.encode()))
    s.send(bytes(b'\xFE'))

def display():
    global s
    s.send(bytes(b'\x00'))
def setCursor(x, y):
    global s
    msg = [1,x,y]
    msg = bytes(msg)
    s.send(msg)

    
def fontSize(size):
    if size == 1:
        sendData(b'\x03')
    elif size == 2:
        sendData(b'\x04')
    elif size == 3:
        sendData(b'\x05')
    else:
        pass
    
     
def sendData(data):
    global s
    if isinstance(data, str):
        data.encode()
    try:
        s.send(bytes(data))
    except:
        pass
def clearScreen():
    global s
    s.send(bytes(b'\x02'))

def loop():
    global delay
    global send
    global angle
    global step
    if send:
        modeCheck()
    angle += step
    if angle > 360:
        angle = 0
#    a = root.clipboard_get()
#    print(a)
    root.after(delay, loop)
    
def end():
    global send
    send = 0
    global s
    s.send(bytes(b'\x09'))
    fontSize(2)
    clearScreen()
    display()
    root.after(1000, break_connection)
def break_connection():
   # global ser
    #ser.close()
    global s
    s.close()
    quit()

 

#==============TK-SETUP=================
frame3 = Frame(root)

frame3.pack(side = BOTTOM)
frame2 = Frame(root)

#Label(text="Mode:").pack(side = BOTTOM)
frame1 = Frame(root)

frame1.pack(side = LEFT)
#frame2.pack(side = TOP)

b2 = Button(frame1, text="X", command=end).pack(side = LEFT)
bv = Button(frame1, text=">", command=toggleMenu)
bv.pack(side = LEFT)
b1 = Button(frame2, text="1", command=toggleSend, relief="sunken")
b1.pack(side = LEFT)


bl = Button(frame2, text="BL", command=toggleBacklight, relief="sunken")
#bl.pack(side=LEFT)

Radiobutton(frame2, text="TD", variable=mode, value=1, indicatoron=0).pack(side = LEFT)
Radiobutton(frame2, text="OV", variable=mode, value=2, indicatoron=0).pack(side = LEFT)
Radiobutton(frame2, text="CB", variable=mode, value=3, indicatoron=0).pack(side = LEFT)
Radiobutton(frame2, text="PB", variable=mode, value=4, indicatoron=0).pack(side = LEFT)

Radiobutton(frame2, text="In", variable=mode, value=0, indicatoron=0).pack(side = LEFT)
inp = StringVar()
inp.set("60")

establishConnection()
if not send:
    b1.configure(relief="raised", text="0")
root.after(1000, loop)
root.mainloop()
