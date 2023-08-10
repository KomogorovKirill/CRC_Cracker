#!/usr/bin/env python3
# -*- coding utf-8 -*-

import argparse
import bitstring

# CRC-64-ECMA polynomial (default value)
polynomial = 0xC96C5795D7870F42
vi = 0
xorout = 0
bit_width = 64
invert_input = False
invert_output = False
crc_length = 0xFFFFFFFFFFFFFFFF
table_forward = [0] * 256
table_reverse = [0] * 256

def CreateCRCtable():
    for i in range(256):
        crc = i
        for j in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= polynomial
            else:
                crc >>= 1
        table_forward[i] = crc

def GetCRCcode(string, crc = vi):
    if invert_input:
        string = [int('{:08b}'.format(ch)[::-1],2) for ch in string.encode()]
    for ch in string:
        crc = table_forward[(crc & 0xff) ^ ord(ch)] ^ (crc >> 8) & crc_length
    if invert_output:
        crc = int('{:08b}'.format(crc)[::-1], 2)
    return crc ^ xorout

def GetCRCreverse(crc, prefix):
    for i in range(256):
        table_reverse[GetCRCcode(chr(i)) >> (bit_width - 8)] = GetCRCcode(chr(i))

    revCRC = []

    for i in range(int(bit_width / 8)):
        highByte = crc >> (bit_width - 8)
        crc ^= table_reverse[highByte]
        crc <<= 8
        revCRC.append(highByte)

    result = ''
    prefixCRC = GetCRCcode(prefix)
    curHighByte = prefixCRC & 0xFF

    for revByte in revCRC[::-1]:
        recovered = table_forward.index(table_reverse[revByte]) ^ curHighByte
        curHighByte = GetCRCcode(result + chr(recovered), prefixCRC) & 0xFF
        result += chr(recovered)
    result = prefix + result

    print(f'Reverse CRC   value (string): {result}')
    print(f'Revers  CRC   value (hex):    {result.encode().hex()}')
    print(f'CRC     check value:          {hex(GetCRCcode(result)).lstrip("0x").rstrip("L")}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Coded from CyberRavenMan')
    parser.add_argument('--crc', help = "crc code", required = True)
    parser.add_argument('--prefix', help = "prefix value", required = False)
    parser.add_argument('--polynom', help = "polynomial for crc", required = False)
    parser.add_argument('--vi', help = "initialization vector in hex format to start calculation (default valie 0)", required = False)
    parser.add_argument('--invert_input', help = "flag, activation of which inverts output value of crc", required = False)
    parser.add_argument('--invert_output', help = "flag, activation of which inverts output value of crc", required = False)
    parser.add_argument('--xor_out', help = "activation of which xor output value of crc", required = False)

    args = parser.parse_args()
    CreateCRCtable()
    if None == args.prefix:
        args.prefix = ''
    if None != args.polynom:
        polynomial = int(args.polynom, 16)
        bits_poly = bitstring.BitArray(hex(polynomial))
        bit_width = len(bits_poly)
        stringMask = "ff" * int(bit_width / 8)
        crc_length = int(stringMask, 16)
    if None != args.vi:
        vi = int(args.vi, 16)
    if None != args.xor_out:
        xorout = crc_length
    if None != args.invert_input:
        invert_input = True
    if None != args.invert_output:
        invert_output = True
    GetCRCreverse(int(args.crc, 16), args.prefix)
