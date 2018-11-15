# _*_ conding: utf-8 _*_
#!/usr/bin/env python3


import asyncio
import logging
import struct
import time


log = logging.getLogger(__name__)


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, callback):
        self.callback = callback

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.info('Connection from {}'.format(peername))
        self.transport = transport
        if self.callback:
            self.callback(self.transport)

    def data_received(self, data):
        message = data.decode()
        log.info('Data received: {!r}'.format(message))

        log.info('Send: {!r}'.format(message))
        self.transport.write(data)

        # log.info('Close the client socket')
        # self.transport.close()


class CapaServer:

    HEAD = 0xEE
    END = 0xED

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop or asyncio.get_event_loop()

        self.connected = None
        self.transport = None
        self.loop.create_task(self._do_connect())

        self.start()

    async def _do_connect(self):
        try:
            server = await loop.create_server(
                lambda: EchoServerProtocol(self.send_data),
                self.host, self.port)
            self.connected = True
            log.info(f'Serving on {server.sockets[0].getsockname()}')
        except Exception as e:
            log.error(f'{e}')

    def send_data(self, transport):
        self.transport = transport

    def start(self):
        # self._auto_loop()
        self._send_dirty()

    def _auto_loop(self):
        import random
        fmt = '>BBBBBBBBBB'
        time_stamp = time.strftime('%y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        pre_time = (int(i) for i in time_stamp.split('-'))
        if self.transport:
            sys = random.randint(1, 10)
            point = random.randint(1, 2)
            message = struct.pack(fmt, self.HEAD, sys, point, *pre_time, self.END)
            self.transport.write(message)
            log.info('Data sent: {!r}'.format(message))
        self.loop.call_later(1, self._auto_loop)

    def _send_dirty(self):
        message = [
            b'\xee\x05\x01\x12\\xee\x0b\x0e\x0f5,\xed\xee\x04\x01\x12',
            b'\x0b\x0e\x0f5-\xed\xee\x03\x09\x02\x12\x0b\x0e\x0f5.\xed'
        ]
        import random
        if self.transport:
            i = random.choice(message)
            self.transport.write(i)
            log.info('Data sent: {!r}'.format(i))
        self.loop.call_later(3, self._send_dirty)


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
    capa_server = CapaServer('0.0.0.0', 8888, loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    loop.close()
