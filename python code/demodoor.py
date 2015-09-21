#!/usr/bin/env python

# Script for LED control demo. 

from cobs_serial import cobs_serial
#from ctypes import c_ulong
from collections import deque

rssi_threshold = 7
rssi_max = 9

header = """
****************************
******** Demo Door *********
****************************
"""

"""
psuedo code:

-set up whitelist(hardcoded?)
-set up data structures based on size of whitelist, (ring buffers, dictonary ie python map)
-begin mainloop
	+read
	+timeout or crc clear?
		-if timeout, "update" each ring buffer with a zero
		-if crc clear, and id is on whitelist, update the ring buffer with that RSSI value


"update(list, value)" places the new value in the list, drops the oldest value, recalculates the average, writes the average to the dictonary, and if that dictonary entry is above open door threshold, fire open door routine.

"opendoor()" behavior tbd, but there are 2 ways of doing it so far (blocking or threads)... 
"""

def main():
	print header
	
	# Open the serial port
	# ************************** USER ENTERED PORT ***************************
	port = raw_input("Enter your serial port (EX: COM14)\n>>")
	cobs = cobs_serial(port, 115200, 1)
	
	# ************************** DEFAULT DEBUG PORT ***************************
	#print "Defaulting port to COM17. Change script if neeeded"
	#cobs = cobs_serial('COM17', 115200, 1)
	
	# *************************** END PORT CONFIG ****************************	
	
	print "Adding hardcoded ID's to whitelist..."
	white1 = 0x0201041B # apparent ID taken from C# code that worked with "observer" code.
								 # (0201041B) in hex = (33621019) in decimal.
								 
	white2 = 0x01010101 # arbitrary second white listed ID
	whitelist = [white1, white2] #list of whitelisted ID's
	
	#print "Whitelisted ID: " + repr(white1)
	print "Whitelist contents: " + repr(list(whitelist))
	#print len(whitelist) #
	
	print "Building data structures..."
	id_map = {}
	
	for id in whitelist:
		id_map[id] = [0, 0, deque([0,0,0,0,0,0,0,0,0,0])] #total, average, values
	
	print id_map
	
	while(True):
		#new_value = int(raw_input()) #simulate getting a message over serial
		#update_map(id_map, 33621019, new_value)
		#print id_map
		retarray = cobs.block_and_return() #this function checks the CRC for us. returns data only, no crc
		if not(retarray == None):
			print repr(retarray)
		#real version
		#timeout read from cobs serial
		#dissect ID / rssi from message, call update_map
		#     c# version used a byte array and the c cobs libraries to convert the bytes

	
def update_map(id_map, id_to_update, new_value, debug = False):
	if not(id_to_update in id_map):
		return
	
	if new_value > rssi_max:
		if debug:
			print("RSSI value recieved that was outside expected ranges. Ignoring.")
		return
	
	temp = id_map[id_to_update][2].popleft() #new value bumps out oldest val
	id_map[id_to_update][0] -= temp
	id_map[id_to_update][0] += new_value #adjust the running total
	id_map[id_to_update][2].append(new_value) #record new value
	
	if id_map[id_to_update][0] > rssi_threshold*10: open_door(id_to_update)		
	
def open_door(id_to_update, debug = False):
	#send cobs frame to open the door
	if debug:
		print("Door opened for ID: " + repr(id_to_update))

	
if __name__ == '__main__':
	main()

#END