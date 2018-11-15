#!/usr/bin/env python3
# _*_ coding: utf-8 _*_


import asyncio
import logging
from collections import namedtuple
import struct


log = logging.getLogger(__name__)


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, master, message, loop, callback):
        self.master = master
        self.message = message
        self.loop = loop
        self.callback = callback

    def connection_made(self, transport):
        self.master.connected = True
        if self.message:
            transport.write(self.message.encode())
            log.info('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        if self.callback:
            self.callback(data)
        log.info('Data received: {!r}'.format(data))

    def connection_lost(self, exc):
        self.master.connected = None
        log.info('The server closed the connection')



class Capadis:

    ALARM = namedtuple('ALARM', 'System Point Time')
    HEAD = 0xEE
    END = 0xED
    MIN_LENGTH = 10
    MIN_DATA_LENGTH = 8

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

        self.connected = None
        self.transport = None

        self.message = []
        self.message_buffer = []

        self.loop.create_task(self._do_connect())

    async def _do_connect(self):
        while True:
            await asyncio.sleep(1)
            if self.connected:
                continue
            message = None
            try:
                transport, protocol = await self.loop.create_connection(
                    lambda: EchoClientProtocol(
                        self, # import the whole of Adam variable
                        message,
                        self.loop,
                        self.parse_data),
                    self.host,
                    self.port)
                log.info('Connection create on {}'.format(transport))
                self.transport = transport
            except OSError:
                log.error('Server not up retrying in 5 seconds...')
            except Exception as e:
                log.error('Error when connect to server: {}'.format(e))

    def parse_data(self, data):
        self.message = []
        self.solve_dirty(data)
        if not self.message:
            return
        try:
            for mesg in self.message:
                if self.is_invalid(mesg):
                    continue
                (sys, point) = struct.unpack('>BB', mesg[1:3])
                (y, m, d, H, M, S) = struct.unpack('>BBBBBB', mesg[3:-1])
                time = '20{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, H, M, S)
                log.info(f'ALARM INFO: --{sys}--{point}--{time}')
        except struct.error as e:
            log.error(f'{e}')

    def is_invalid(self, mesg):
        if len(mesg) != self.MIN_LENGTH:
            return True
        s = struct.Struct('>B')
        (head,) = s.unpack(mesg[:1])
        (end,) = s.unpack(mesg[-1:])
        if head != self.HEAD or end != self.END:
            return True
        return False

    def solve_dirty(self, data):
        x_indexs = []
        x_bytes = b''
        for i in range(len(data)):
            if data[i] == self.HEAD or data[i] == self.END:
                x_indexs.append(i)
        if data[x_indexs[0]] == self.END:
            x = data[:x_indexs[0]+1]
            if len(self.message_buffer) > 0:
                self.message_buffer.append(x)
        for j in range(len(x_indexs)-1):
            if data[x_indexs[j]] == self.HEAD and data[x_indexs[j+1]] == self.END:
                x = data[x_indexs[j]:x_indexs[j+1]+1]
                self.message.append(x)
        if data[x_indexs[len(x_indexs)-1]] == self.HEAD:
            x = data[x_indexs[len(x_indexs)-1]:]
            if len(self.message_buffer) > 0:
                self.message_buffer = []
            self.message_buffer.append(x)
        for i in self.message_buffer:
            x_bytes += i
        if self.HEAD in x_bytes and self.END in x_bytes:
            self.message.append(x_bytes)


if __name__ == "__main__":
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    loop = asyncio.get_event_loop()
    capadis = Capadis('0.0.0.0', 8888, loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
