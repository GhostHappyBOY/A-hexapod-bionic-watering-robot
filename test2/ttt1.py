import serial    #import serial module
ser = serial.Serial('/dev/ttyUSB0', 115200)   #open named port at 9600,1s timeot

#try and exceptstructure are exception handler
while 1:
    ser.write('s'.encode())  #writ a string to port
    response = ser.read_all()   #read a string from port
    print(response)
