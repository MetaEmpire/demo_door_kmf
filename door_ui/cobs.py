import serial
import binascii
import struct
import random

class cobs:
	#-------------------------------------------------------------------------------------------------#
	#                                        cobs encoder                                             #
	#-------------------------------------------------------------------------------------------------#
		
	def build_frame(self,indata): #returns a cobs frame with a ckecksum on the end from the passed in data
		framedat = indata
		framedat += self.crc32_checksum(indata)
		outdat = self.encode_cobs(framedat, len(framedat))
		return outdat
		
	def crc32_checksum(self,encdata): #generates a 32bit checksum, converts it to bytes, and returns the resulting array
		checksum = binascii.crc32(encdata)
		bytcheck = struct.pack('>i', checksum)
		return bytcheck
		
	def encode_cobs(self,indata,data_len): #encodes the actual cobs data and returns the result
		outframe = bytearray(len(indata)+1)
		z_offset = 0
		offset = 1
		while offset < (data_len+1):
			if indata[offset-1] == 0:
				outframe[z_offset] = (offset-z_offset)
				z_offset = offset
				outframe[z_offset] = 0
			else:
				outframe[offset] = indata[offset-1]
			offset +=1
		outframe[z_offset] = (offset-z_offset)
		return outframe


	#--------------------------------------------------------------------------------------------------#
	#                                        cobs decoder                                              #
	#--------------------------------------------------------------------------------------------------#
		
	def decode_and_check(self,data): #disassembles the frame and tests the checksum, returns the array if its good
		dec = self.decode_cobs(data)
		testchk = self.test_checksum(dec)
		return testchk[0:len(testchk)-5]
		
	def decode_cobs(self,indata): #decodes the cobs frame and returns the result
		offset = 0
		length = len(indata)
		outdata = bytearray(255)
		if length >= 255:
			x = 1/0
		while offset < length:
			block = indata[offset]
			if block == 0:
				#print "too short"
				return None
			if (offset+block)>length:
				#print "too long"
				return None
			outdata[offset:offset + block-1] = indata[offset+1:offset+1+block-1]
			offset +=block
			if offset < length:
				outdata[offset-1] = 0
		outdata[offset-1] = 0
		return outdata[0:offset]
			
	def test_checksum(self,indata): #unpacks and tests the checksum to make sure the frame is valid
		datchecksum = binascii.crc32(indata[0:len(indata)-5])
		sentchecksum = struct.unpack('>i', indata[len(indata)-5:len(indata)-1])
		if datchecksum == sentchecksum[0]:
			return indata
		else:
			return None
#----------------------------------------------------------------------------------------------------------#
#                    this beats on the cobs algorithm to make sure everything works			               #
#----------------------------------------------------------------------------------------------------------#
class test_cobs:
	encerrors = 0
	decerrors = 0
	comperrors = 0
	encoder = cobs()

	def cobstest(self): #generates a random frame, encodes, decodes, then checks to make sure it matches
		framesize = random.randint(1,249)
		randframe = bytearray(random.sample(xrange(255),framesize))
		encframe = self.encoder.build_frame(randframe)
		#print randframe
		if encframe == None:
			encerrors+=1	
		decframe = self.encoder.decode_cobs(encframe)
		if decframe == None:
			decerrors +=1
		if randframe != decframe[0:len(decframe)-1]:
			comperrors +=1

	def printerrors(self): #print the number of errors generated
		print"encode errors: ",
		print self.encerrors
		print "decode errors: ",
		print self.decerrors
		print "comparison errors: ",
		print self.comperrors
		print "total errors: ",
		print self.encerrors+self.decerrors+self.comperrors
		
	def mass_test(self,number): #runs the test <number> number of times and prints the result
		for i in range(0,number):
			self.cobstest()
			if i%(number/10) == 0:
				print "number of tests run: ",
				print i
				self.printerrors()
		self.printerrors()
	
if __name__ == '__main__':
	tester = test_cobs()
	tester.mass_test(100)
	