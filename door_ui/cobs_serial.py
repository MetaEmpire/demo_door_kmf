import serial
import random
import time
import sys
from cobs import cobs as encoder

class cobs_serial:
	ser = 0
	cobs = 0
	
	#----------------------------------------------------------------------------------------------------------#
	#                     creates the serial object required by all functions in this file                     #
	#----------------------------------------------------------------------------------------------------------#
	
	def __init__(self,port,baud,to):#upon object creation, opens a serial port
		self.cobs = encoder()
		try:
			self.ser = serial.Serial(port,baud,timeout = to)
		except:
			return None
	
	#----------------------------------------------------------------------------------------------------------#
	#                                           cobs uart sender                                               #
	#----------------------------------------------------------------------------------------------------------#
	
	def encode_and_send(self,data):#takes data in, generates a cobs frame and then stuffs it out the serial port
		try:
			send = bytearray('\0')
			send += self.cobs.build_frame(data)
			send += '\0'
			#print repr(send)
			#print
		except:
			#print "error encoding packet, packet may be too long or of the incorrect type"
			return None
		self.ser.write(send)
		return 1
	
	#-----------------------------------------------------------------------------------------------------------#
	#                                           cobs uart receiver                                              #
	#-----------------------------------------------------------------------------------------------------------#
	
	def read_and_build(self):#loops on the serial port waiting for and building up data
		rawdat = bytearray(255)
		offset = 0
		self.ser.read()
		while True:
			inbyte = self.ser.read()
			#print repr(inbyte)
			if inbyte != '\0':
				if offset == 250:
					return None
				rawdat[offset] = inbyte
				offset+=1
				continue
			if offset < 5:
				return None
			break
		return rawdat[0:offset]
	
	def block_and_return(self):#calls the functions required to read and build the cobs frame
		try:
			got = self.read_and_build()
			return self.cobs.decode_and_check(got)
		except:
			return None
			
	#------------------------------------------------------------------------------------------------------#
	#                                       object's port closer                                           #
	#------------------------------------------------------------------------------------------------------#
		
	def close_port(self):
		self.ser.close
#----------------------------------------------------------------------------------------------------------#
#                    this beats on the serial stuff to make sure everything works			               #
#----------------------------------------------------------------------------------------------------------#
class test_cobs_serial:
	cobs = 0
	dropped = 0
	def __init__(self,port,baud,to):
		self.cobs = cobs_serial(port,baud,to)
	
	def test_uart(self): #generates a random frame and sends it to the serial portion of the library then gets a frame back and checks to see if its good
		framesize = random.randint(1,245)
		randframe = bytearray(random.sample(xrange(256),framesize))
		self.cobs.encode_and_send(randframe)
		got = self.cobs.block_and_return()
		if randframe[0:framesize] != got:
			self.dropped+=1
			#print "sent: "
			#print "  ",repr(randframe)
			#print "got: "
			#print "  ",repr(got)
			
	def printerrors(self): #prints the total number of dropped frames to the command line
		print "total dropped frames: ",
		print self.dropped
	
	def mass_test(self,number):#this takes in a number of tests to run, runs them, and spits out the results
		for i in range(0,number):
			self.test_uart()
			time.sleep(0.020)
			if i%(number/10) == 0:
				print "number of tests run: ",
				print i
				self.printerrors()
		self.printerrors()
		#self.cobs.close_port()
		
if __name__ == '__main__':
	tester = test_cobs_serial(int(sys.argv[1]),int(sys.argv[2]),float(sys.argv[3]))
	tester.mass_test(int(sys.argv[4]))