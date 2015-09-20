#!/usr/bin/env python

# Script for LED control demo. 

from cobs_serial import cobs_serial
#from ctypes import c_ulong
from collections import deque

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

"opendoor()" behavior tbd, but there are 2 ways of doing it so far... 
"""

def main():
	print header
	
	print "Adding hardcoded ID's to whitelist..."
	white1 = 0x0201041B # apparent ID taken from C# code that worked with "observer" code.
								 # (0201041B) in hex = (33621019) in decimal.
								 
	white2 = 0x01010101 # arbitrary second white listed ID
	whitelist = [white1, white2] #list of whitelisted ID's
	
	#print "Whitelisted ID: " + repr(white1)
	print "Whitelist contents: " + repr(list(whitelist))
	#print len(whitelist) #
	
	print "Building data structures..."
	id_rssi_map = {}
	
	for id in whitelist:
		id_rssi_map[id] = 0
	
	print id_rssi_map
	
	#id_rssi_map[7] = whitelist #seems to work fine?
	#list for each ID...
	#list of these lists?
	#another map? key being the ID, the list being the value?
	
	'''
	operations needed for this list
		-pop oldest value
		-push newest value
		-use both of those values to adjust the running total (to then adjust the running average)
	
	summary of thoughts: use deque for the list
	use 3 maps for all data structure needs
	ID/running-average map
	ID/deque map
	ID/running-total map
	
	object?
	
	new notes, map of ID/tuples. each tuple is [deque of numbers, running total, running average]
	can index through list like "for each_id in this_map: 
									if each_id[2] > rssi_threshold.....
	'''
	
	
if __name__ == '__main__':
	main()

#END