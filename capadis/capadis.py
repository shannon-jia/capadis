# -*- coding: utf-8 -*-

"""Main module."""


import logging
import struct


log = logging.getLogger(__name__)


class Capadis:

    """
    Capadis Message Type:

      Capacitance disturbance alarm system supports TCP/IP message transmission type.

      Communication with external system through socket mode of TCP/IP protocol.

    Communication diagrams:

    .. image:: /puml.png

    """
    HEAD = 0xEE
    END = 0xED
    MIN_LENGTH = 10

    """
    Conventions:

      Bytes are in hexadecimal.

      The total length of the data is 10.

      Bytes 1 is packet header, equal to EE.

      Bytes 2 is Zone.

      Bytes 3 is upper and lower three-line mark.
        01 is the upper three line.
        02 is the lower three line.

      Bytes 4 is year.

      Bytes 5 is month.

      Bytes 6 is day.

      Bytes 7 is hour.

      Bytes 8 is minute.

      Bytes 9 is second.

      Bytes 10 is packet end, equal to ED.

    """

    def __init__(self):
        self.message_buffer = []

    def received(self, data):

        """
        Receiving Alarm Information from Capacitance Disturbance Alarm System.
        """

        message = self.solve_dirty(data)
        if not message:
            return
        self.parse(message)
        return True

    def parse(self, message):

        """
        Analysis and unpacking of alarm messages received.
        """

        try:
            for mesg in message:
                if self.is_invalid(mesg):
                    continue
                (sys, point) = struct.unpack('>BB', mesg[1:3])
                (y, m, d, H, M, S) = struct.unpack('>BBBBBB', mesg[3:-1])
                time = '20{:02d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(y, m, d, H, M, S)
                log.info(f'ALARM INFO: --{sys}--{point}--{time}')
        except struct.error as e:
            log.error(f'{e}')

    def is_invalid(self, mesg):

        """
        Determine whether the data received is valid.
        """

        if len(mesg) != self.MIN_LENGTH:
            return True
        if mesg[0] != self.HEAD or mesg[-1] != self.END:
            return True
        return False

    def solve_dirty(self, data):

        """
        Extracting effective data from dirty data.
        """

        message = []
        d_indexs = []
        d_buff = b''
        for _index in range(len(data)):
            if data[_index] == self.HEAD or data[_index] == self.END:
                d_indexs.append(_index)
        self._deal_head(data, d_indexs)
        message = self._deal_body(data, d_indexs)
        self._deal_tail(data, d_indexs)
        for msg in self.message_buffer:
            d_buff += msg
        if self.HEAD in d_buff and self.END in d_buff:
            message.append(d_buff)
        return message

    def _deal_head(self, data, d_indexs):
        _first = d_indexs[0]
        if data[_first] == self.END:
            _x = data[:_first+1]
            if len(self.message_buffer) > 0:
                self.message_buffer.append(_x)

    def _deal_body(self, data, d_indexs):
        _mesg = []
        for i in range(len(d_indexs)-1):
            _this = d_indexs[i]
            _next = d_indexs[i+1]
            if data[_this] == self.HEAD and data[_next] == self.END:
                _x = data[_this:_next+1]
                _mesg.append(_x)
        return _mesg

    def _deal_tail(self, data, d_indexs):
        _last = d_indexs[-1]
        if data[_last] == self.HEAD:
            _x = data[_last:]
            if len(self.message_buffer) > 0:
                self.message_buffer = []
            self.message_buffer.append(_x)


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

    capadis = Capadis()
    x = b'\xee\x03\x09\x12\x0b\x0e\x0f5.\xed'
    x1 = b'\xee\x04\x01'
    x2 = b'\x12\x0b\x0e\x0f5-\xed'
    r1 = capadis.received(x1)
    r2 = capadis.received(x2+x)
    print(r1)
    print(r2)
