#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from collections import namedtuple
import logging
import threading

import serial

"""
Python Numeric Broadcast Protocol

This module implements HP Tuners / Track Addict Numeric Broadcast Protocol
"""

__version__='0.0.5'
logger = logging.getLogger(__name__)
NbpKPI = namedtuple('NbpKPI', 'name, unit, value')
NbpPayload = namedtuple('NbpPayload', 'timestamp, packettype, nbpkpilist')

class PyNBP(threading.Thread):
    def __init__(self, nbpqueue, device='/dev/rfcomm0', device_name='PyNBP', protocol_version='NBP1', min_update_interval=0.2):
        self.device = device
        self.device_name = device_name
        self.protocol_version = protocol_version
        self.reftime = time.time()
        self.last_update_time = 0
        self.packettime = 0
        self.kpis = {}
        self.nbpqueue = nbpqueue
        self.updatelist = []
        self.min_update_interval = min_update_interval
        threading.Thread.__init__(self)


    def run(self):
        connected=False
        serport=None

        while True:
            nbppayload = self.nbpqueue.get()

            self.packettime = nbppayload.timestamp

            for kpi in nbppayload.nbpkpilist:
                if kpi.name not in self.updatelist:
                    self.updatelist.append(kpi.name)
                self.kpis[kpi.name] = kpi

            if not connected:
                try:
                    serport=serial.serial_for_url(self.device)
                    connected=True
                except:
                    logging.warning('Comm Port conection failed - waiting for connection')

            if connected and serport.is_open:
                try:
                    if time.time() - self.last_update_time > self.min_update_interval:
                        if nbppayload.packettype == 'UPDATE':
                            nbppacket=self._genpacket(type=nbppayload.packettype)
                        elif nbppayload.packettype == 'ALL':
                            nbppacket=self._genpacket(type=nbppayload.packettype)
                        elif nbppayload.packettype == 'METADATA':
                            nbppacket=self.metedata()
                        else:
                            logging.warning('Invalid packet type {0}.'.format(packettype))

                        logging.warning(nbppacket)

                        serport.write(nbppacket)
                        self.updatelist = []
                        self.last_update_time = time.time()

                except:
                    logging.exception('Serial Write Failed. Closing port.')
                    serport.close()
                    connected = False


    def metedata(self):
        return str.encode("@NAME:{0}\n".format(self.device_name))

    def _genpacket(self, type='ALL'):
        reltime = self.packettime - self.reftime
        packet="*{0},{1},{2:.6f}\n".format(self.protocol_version, type, reltime)

        if self.updatelist and type != 'ALL':
            kpis = [self.kpis[k] for k in self.updatelist]
        else:
            kpis = self.kpis.values()


        for kpi in kpis:
            if kpi.unit:
                packet+='"{0}","{1}":{2}\n'.format(kpi.name, kpi.unit, kpi.value)
            else:
                packet+='"{0}":{1}\n'.format(kpi.name, kpi.value)

        packet+="#\n"

        return str.encode(packet)

