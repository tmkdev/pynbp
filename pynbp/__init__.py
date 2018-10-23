#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from collections import namedtuple
import logging
import threading
import random

import serial

logger = logging.getLogger(__name__)

name='pynpb'

NbpKPI=namedtuple('NbpKPI', 'name, unit, value')

class PyNBP(threading.Thread):
    def __init__(self, nbpqueue, device='/dev/rfcomm0', device_name='PyNBP', protocol_verion='NBP1'):
        self.device = device
        self.device_name = device_name
        self.protocol_verion = protocol_verion
        self.reftime = time.time()
        self.kpis = {}
        self.nbpqueue = nbpqueue
        threading.Thread.__init__(self)


    def run(self):
        connected=False
        serport=None

        while True:
            nbpkpis, packettype = self.nbpqueue.get()

            updatelist = []
            for kpi in nbpkpis:
                updatelist.append(kpi.name)
                self.kpis[kpi.name] = kpi

            if not connected:
                try:
                    serport=serial.Serial(self.device)
                    connected=True
                except:
                    logging.warning('Comm Port conection failed - waiting for connection')

            if connected and serport.is_open:
                if packettype in ['UPDATE']:
                    nbppacket=self._genpacket(kpilist=updatelist, type=packettype)
                elif packettype in ['ALL']:
                    nbppacket=self._genpacket(kpilist=None, type=packettype)
                elif packettype in ['METADATA']:
                    nbppacket=self.metedata()
                else:
                    logging.warning('Invalid packet type {0}.'.format(packettype))

                logging.debug(nbppacket)

                try:
                    serport.write(nbppacket)
                except:
                    logging.critical('Serial Write Failed. Closing port.')
                    serport.close()
                    connected = False


    def metedata(self):
        return str.encode("@NAME:{0}\n".format(self.device_name))

    def _genpacket(self, type='ALL', kpilist=None):
        reltime = time.time() - self.reftime
        packet="*{0},{1},{2:.3f}\n".format(self.protocol_verion, type, reltime)

        if kpilist:
            kpis = [ self.kpis[k] for k in kpilist]
        else:
            kpis = self.kpis.values()


        for kpi in kpis:
            if kpi.unit:
                packet+='"{0}","{1}":{2}\n'.format(kpi.name, kpi.unit, kpi.value)
            else:
                packet+='"{0}":{1}\n'.format(kpi.name, kpi.value)

        packet+="#\n"

        return str.encode(packet)

