#==============IMPORTS==================

from tkinter import *
import socket, sys, os, time, psutil, subprocess, ctypes


#==============CONSTANTS================
root = Tk()
root.overrideredirect(True)
root.withdraw()
root.deiconify()
#root.title("ESPER-GUI")
send = True
host = '192.168.1.*'# <--Your IP goes here
port = 8888
mode = IntVar()
mode.set(2)
delay = 250 #<-- Adjust it so the screen doesn't flicker
cur = 0
preva = "                "
prevb = "                "
lilcounter = 0
backlight = True
prevmode = 2
menu = False


#==============FUNCTIONS================

def center(x): # A function to center displayed text (I was just too lazy to do it myself)	
	x = str(x)
	spaces = (16 - len(x))/2 #Get half of the empty space...
	x = " "*int(spaces)+ x # and fill it with spaces.
	return x #Return and Done!


def correctLength(x):
	if len(x) == 1: #Just to make sure the value is 2 characters long
		x = "0" + x
	elif len(x) > 2:
		x = "1c"
	return(x)
	
	
def modeCheck():
	global mode
	global lilcounter
	global prevmode
	
	if not mode.get() == prevmode:
		clearScreen()
	if mode.get() == 0: #Display version message
		modeInfo()
		
	elif mode.get() == 1: # Simple clock and date
		modeClock()
		
	elif mode.get() == 2: #This is an overview of computer's satus like RAM CPU (also time+date)
		modeOverview()
		
	elif mode.get() == 3:#display clipboard content
		modeClipboard()
		
	elif mode.get() == 4: #timer, counts down 60 seconds
		modeTimer()
		
	lilcounter += 1
	if lilcounter == 4:
		lilcounter = 0
	prevmode = mode.get()


def modeInfo(): #Display the version
	encodeData("*  ESPER v2.0  *", "*  Connected!  *")

	
def modeClock(): #Display a simple clock
	global lilcounter
	a = center(time.strftime("%H:%M:%S", time.localtime()))
	b = center(time.strftime("%d.%m.%y", time.localtime()))
	encodeData(a, b)
	sendData(15, 0, bytearray(wheelCounter(lilcounter))[0])
	sendData(0, 0, bytearray(wheelCounterReverse(lilcounter))[0])


def modeOverview(): #Display an overview of your computer
	global lilcounter
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
#		if lstates[64] == "n":
#			scrol = "S"
#		else:
#			scrol = "s"
		temp = str(int(psutil.sensors_temperatures()["coretemp"][1].current))
	elif os.name == 'nt':
		hllDll = ctypes.WinDLL ("User32.dll")
		VK_CAPITAL = 0x14
		VK_NUMLOCK = 0x90
		if hllDll.GetKeyState(VK_CAPITAL):
			caps = "A"
		else:
			caps = "a"
		if hllDll.GetKeyState(VK_NUMLOCK):
			num = "N"
		else:
			num = "n"

		temp = "??"
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
	

	a = str(time.strftime("%H:%M", time.localtime())) + "C" + correctLength(cpu) + "T" + correctLength(temp) + "B" + correctLength(bat)+ caps+ num
	b = str(time.strftime("%d/%m", time.localtime())) + "R" +  correctLength(ram) +"S"+ correctLength(swap) + "D"+ correctLength(disk) +" " +str(lilcounter)
	sendData(14, 1, bytearray(wheelCounter(lilcounter))[0])
	
	encodeData(a, b)


def modeClipboard(): #Display the conent of your clipboard
	clip = root.clipboard_get()
	if len(clip) < 17:
		a = clip
		b = ""
	elif len(clip) > 17 or len(clip) == 16:
		a = clip[0:16]
		if len(clip) < 32:
			b = clip[16:]
		else:
			b = clip[16:32]
	encodeData(a, b)

	
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
	progressBar(cur, total)
	cur += 1
	if cur > total:
		cur = 0
		mode.set(2)


def dialogBox(): #set timer
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


def dialogClose(event): #close the dialog box
	global dialog
	dialog.destroy()
	
	
def progressBar(cur, total):#Display a progress bar
	bars = int(round(cur/total*16, 0))
	a = correctLength(str(round(cur/total*100)))+ "% " +str(int(cur*delay/1000))+"/"+str(int(total*delay/1000) )
	if bars > 0:
		sendData(bars-1,1, 255)
	#b = "" * bars + "." * (16-bars)
	encodeData(center(a), "")
		
	
def wheelCounter(val):#a loading wheel
	if val == 0:
		return b"|"
	elif val == 1:
		return b"/"
	elif val == 2:
		return b"-"
	elif val == 3:
		return b"\x00"


def wheelCounterReverse(val):#same as above, but the other way around
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
	print("Creating socket")
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
	send = not send
	if send:
		b1.config(relief="sunken", text="1")
		
	elif not send:
		b1.config(relief="raised", text="0")


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
	
	
def encodeData(a, b):
	global s
	global preva
	global prevb
	changes = []
	while len(a) < 16:
		a += " "
	
	while len(b) < 16:
		b += " "
	
	for i in range(16):
		if not a[i]==preva[i]:
			changes.append([i,0, a[i].encode()])
		
		if not b[i]==prevb[i]:
			changes.append([i,1, b[i].encode()])
	if len(changes) > 0:
		print(changes)
	for i in changes:
		
		sendData(int(i[0]), int(i[1]), bytearray(i[2])[0])

	preva = a
	prevb = b
			
	 
def sendData(x, y, data):
	global backlight
	global s
	msg = bytearray(b'\x00\x00')
	msg[0] += backlight*32
	msg[0] += y *16
	msg[0] += x
	msg[1] = data
	msg = bytes(msg)
	s.send(msg)

def clearScreen():
	global preva
	global prevb
	preva = "                "
	prevb = "                "

	for y in range(2):
		for x in range(16):
			sendData(x, y, 160)
def loop():
	global delay
	global send
	if send:
		modeCheck()
#	a = root.clipboard_get()
#	print(a)
	root.after(delay, loop)
	
def end():
	global s
	encodeData(center("ESPER spiritual"), center("connection lost"))
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
bl.pack(side=LEFT)

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
