# -*- coding: utf-8 -*-
import socket
from mercury206.protocol import pack_msg, unpack_msg
from mercury206.utils import digitize, digitized_triple, pretty_hex


HOST = '192.168.153.195'
PORT = 5010
ADDRESS_MERCURY = 18865213
TIMEOUT = 2


def readDataFromSocket(s):
    data = ''
    buffer = ''
    try:
        while True:
            s.settimeout(TIMEOUT)
            data = s.recv(1)
            if data:
                buffer += data
                s.settimeout(None)
    except Exception, error:
        print 'Error', error

    print pretty_hex(buffer)
    s.settimeout(None)
    return buffer


def send_tcp_command(s, address_mercury, command, *params, **kwargs):
    message = pack_msg(address_mercury, command, *params, crc=kwargs.get('crc', True))
    s.sendall(message)
    answer = readDataFromSocket(s)
    answer_lines = answer.split('\r\n')
    answer = ''.join(answer_lines)
    print pretty_hex(answer)
    if len(answer) > 4:
        received_address, received_data = unpack_msg(answer)
        if received_address == address_mercury:
            return received_data


def connect(s, address_mercury):
    result = []
    result.append(send_tcp_command(s, address_mercury, 0x28))
    result.append(send_tcp_command(s, address_mercury, 0x2F, crc=False))


def instant_vcp(s, address_mercury, cmd=0x63):
    """Возвращает список с текущими показаниями напряжения (В),
    тока (А), потребляемой мощности (кВт/ч)"""
    data = send_tcp_command(s, address_mercury, cmd)

    voltage = digitize(data[1:3]) / 10.
    current = digitize(data[3:5]) / 100.
    power = digitize(data[5:8]) / 1000.
    return voltage, current, power


def display_readings(s, address_mercury, cmd=0x27, *args):
    """Возвращает список показаний потреблённой энергии в кВт/ч по 3 тарифам
    с момента последнего сброса"""
    data = send_tcp_command(s, address_mercury, cmd, *args)

    return digitized_triple(data)


if __name__== "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    connect(s, ADDRESS_MERCURY)
    voltage, current, power = instant_vcp(s, ADDRESS_MERCURY)
    print voltage, current, power
    data = display_readings(s, ADDRESS_MERCURY)
    print data