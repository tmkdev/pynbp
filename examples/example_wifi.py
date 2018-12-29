import logging
import time
import random
import queue

from pynbp import *

#pynbp runs in a thread and takes inputs from a queue. The queue payload is a type, with a list of NbpKPI named tuples and a packet type
# UPDATE - Incremental
# ALL - Send all kpis
# METADATA - send only metadata packet
nbp_queue=queue.Queue()

#pynbp needs serial device (Bluetooth) to communicate to track addict.
mypynbp = WifiPyNBP(ip='127.0.0.1', port=35000, nbpqueue=nbp_queue, device_name='Testing')

# Set as a daemon thread so it terminates when the main does
mypynbp.daemon = True
# Start the thread. It will process incoming packets as they get dumped onto the queue.
mypynbp.start()

testkpis = [
        NbpKPI(name='Battery', unit="V", value=random.random()*12.0),
        NbpKPI(name='Steering Wheel', unit="deg", value=random.randint(-360, 360)),
        NbpKPI(name='Gear', unit=None, value=random.randint(1,6)),
]

payload = NbpPayload(timestamp=time.time(), packettype='UPDATE', nbpkpilist=testkpis)

nbp_queue.put(payload)

#Update interval is defaulted to 0.2s so these test sends need to be spaced out longer then 0.2s
time.sleep(0.3)

types = [ 'ALL', 'UPDATE']

#Loop test for update interval 
for i in range(40):
        testkpis = [
                NbpKPI(name='Battery', unit="V", value=random.random()*12.0),
                NbpKPI(name='Gear', unit=None, value=random.randint(1,6)),
        ]
        payload = NbpPayload(timestamp=time.time(), packettype=types[i%2], nbpkpilist=testkpis)
        nbp_queue.put(payload)

        time.sleep(0.03)

payload = NbpPayload(timestamp=time.time(), packettype='ALL', nbpkpilist=[])
time.sleep(0.3)
nbp_queue.put(payload)

payload = NbpPayload(time.time(), packettype='METADATA',  nbpkpilist=[])

time.sleep(0.3)
nbp_queue.put(payload)
time.sleep(0.1)
