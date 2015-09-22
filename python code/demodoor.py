#!/usr/bin/env python

# Script for door demo.

#Imports
from cobs_serial import cobs_serial
#from ctypes import c_ulong
from collections import deque
import struct

#Rssi expected value configuations
rssi_threshold = -20.0
rssi_max = 0

init_rssi_avg = -100.0

#notes on ranges for psoc4 BLE devkits, 12 inches away, unaligned, the rssi fluctuates from -66 to -48.
# aligned and almost touching ( < 1 inch) is about  -5

#Wire protocol constants
id_start_byte = 5
id_stop_byte = 9

rssi_start_byte = 4
rssi_stop_byte = 5

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

def main(debug = False):
	print header
	
	# Open the serial port
	# ************************** USER ENTERED PORT ***************************
	#port = raw_input("Enter your serial port (EX: COM14)\n>>")
	#cobs = cobs_serial(port, 115200, 1)
	
	# ************************** DEFAULT DEBUG PORT ***************************
	print "Defaulting port to COM12. Change script if needed"
	cobs = cobs_serial('COM12', 115200, 1)
	
	# *************************** END PORT CONFIG ****************************	
	
	print "Adding hardcoded ID's to whitelist..."
	white1 = 0x0201041B # apparent ID taken from C# code that worked with "observer" code.
								 # (0201041B) in hex = (33621019) in decimal.
								 
	white2 = 0x01010101 # arbitrary second white listed ID
	whitelist = [white1, white2, 10506251] #list of whitelisted ID's
	
	#print "Whitelisted ID: " + repr(white1)
	print "Whitelist contents: " + repr(list(whitelist))
	#print len(whitelist) #
	
	print "Building data structures..."
	id_map = {}
	
	for id in whitelist:
		id_map[id] = [init_rssi_avg, -1000, deque([init_rssi_avg,init_rssi_avg,init_rssi_avg, \
					init_rssi_avg,init_rssi_avg,init_rssi_avg,init_rssi_avg,init_rssi_avg, \
					init_rssi_avg,init_rssi_avg])] #total, average (UNUSED ATM), values (10 total)
	
	if debug: 
		print id_map
	
	while(True):
		#below read has a timeout of 1 second?
		retarray = cobs.block_and_return() #this function checks the CRC for us. returns data only, no crc
		if not(retarray == None):
			rssi_number = struct.unpack('b', retarray[rssi_start_byte:rssi_stop_byte])
			id_number = struct.unpack('>L', retarray[id_start_byte:id_stop_byte])
			
			#if debug:
				#print "Recieved byte array:\n" + repr(retarray)
				#print "ID bytes: " + repr(retarray[id_start_byte:id_stop_byte])
				#print "RSSI bytes: " + repr(retarray[rssi_start_byte:rssi_stop_byte]) + "\n"
			if debug:
				print "\nID number = " + repr(id_number[0])
				print "RSSI number = " + repr(rssi_number[0])
				
			#if id_number in id_map:   #currently the update_map function implements this behavior
			update_map(id_map, id_number[0], rssi_number[0], cobs, debug)
			#update_map(for any badge that didnt show up, record a "i didnt see this badge" value?)
			
		#else: 						   #since they didnt show up, record a "i didnt see this badge" value
			#for id in id_map.getKeys() 
				#update_map(id_map, id, -100, cobs, debug)
	
def update_map(id_map, id_to_update, new_value, cobs, debug = False):
	if not(id_to_update in id_map):
		return
	
	if new_value > rssi_max:
		if debug:
			print("RSSI value recieved that was outside expected ranges. Ignoring.")
		return
	
	temp = id_map[id_to_update][2].popleft() #new value bumps out oldest val
	id_map[id_to_update][1] -= temp
	id_map[id_to_update][1] += new_value #adjust the running total
	id_map[id_to_update][2].append(new_value) #record new value into queue
	
	if debug:
		print("Updated white-listed ID #" + repr(id_to_update) + ", new running total = " + repr(id_map[id_to_update][1]))
		print "Contents of above ID (last 10 values): " + repr(list(id_map[id_to_update][2]))
	
	if id_map[id_to_update][1] > rssi_threshold*10: open_door(id_to_update, cobs, debug)		
	
def open_door(id_to_update, cobs, debug = False):
	open_door_command = bytearray([0x0, 0x6, 0x0, 0x0]) #mimicing MSFT command for opening door.
	cobs.encode_and_send(open_door_command) #send cobs frame to open the door
	if debug:
		print("Door opened for ID: " + repr(id_to_update))

	
if __name__ == '__main__':
	main(True)

#END
