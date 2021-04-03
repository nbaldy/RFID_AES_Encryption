# Computer Networks Project
# Nicole Baldy and Elena Falcione
# Python/PC portion of an RFID reader + encryption
# This file implements the AES encryption method in python to encrypt/decrypt information to send over the serial port to the Arduino. 
# It should be run by the console using "python3 LaptopCode.py". 
# It was developed using python 3.7.10 on Win10. PySerial and Galois must be installed.

import serial
import numpy as np
import math

ser = None

# S-boxes from online(https://en.wikipedia.org/wiki/Rijndael_S-box)
Sbox = (
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
        )
Sbox_inv = (
        0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
        0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
        0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
        0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
        0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
        0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
        0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
        0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
        0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
        0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
        0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
        0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
        0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
        0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
        0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
        0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D
        )


def MultGF8(byte1, byte2):
    # based on http://www.herongyang.com/Cryptography/AES-MixColumns-Procedure-Algorithm.html
    # With some help my looking at https://gist.github.com/bonsaiviking/5571001 to fix mistakes

    result = 0
    shifted_byte1 = byte1
    shifted_byte2 = byte2
    for i in range(8):
        # Multiply byte1 by byte2 by adding (xor) [byte2] [byte1] times
        # Is the same as adding byte2 << i if byte1[bit i] is 1
        if (0x1 & shifted_byte1):
            result ^= shifted_byte2
        shifted_byte2 = shifted_byte2 << 1 
        # Ensure this remains in GF8 by xor'ing the shifted byte 2 by 0x11b if bit 8 is 1
        if (0x100 & shifted_byte2):
            shifted_byte2 ^= 0x11B
        shifted_byte1 = shifted_byte1 >> 1

    

    # modulo by 0x11b
    return result


def loadInto4x4Bytes(arr16Bytes):
    bytes4x4 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    for row in range(0,4):
        for col in range(0,4):
            if len(arr16Bytes) is 0:
                continue # Keep 0
            bytes4x4[row][col] = arr16Bytes[0]
            arr16Bytes = arr16Bytes[1:]
    return bytes4x4


def unload4x4BytesToArr(data4x4):
    resultArr =[]
    for row in range(0,4):
        for col in range(0,4):
            resultArr.append(data4x4[row][col])
    return resultArr

def addRoundKey(data4x4, key4x4):
    for row in range(0,4):
        for col in range(0,4):
            data4x4[row][col] = data4x4[row][col] ^ key4x4[row][col]
    return data4x4

def subBytes(data, substitution):
    for row in range(len(data)):
        if type(data[row]) is list:
            for col in range(len(data[row])):
                data[row][col] = substitution[data[row][col]]
        else:
            data[row] = substitution[data[row]]
    return data
        
def shiftRows(data4x4):
    # Each row shifted row_num to left
    new_data4x4 = []
    for i in range(4):
        new_data4x4.append(data4x4[i][i:] + data4x4[i][:i])
    return new_data4x4

def invShiftRows(data4x4):
    # Each row shifted row_num to right
    new_data4x4 = []
    for i in range(4):
        new_data4x4.append(data4x4[i][-i:] + data4x4[i][:-i])
    return new_data4x4

def mixCols(data4x4):
    # Advice found on http://www.herongyang.com/Cryptography/AES-MixColumns-Procedure-Algorithm.html
    # Could not get the galois library to compile so see MultGF2 function above, it is cited.
    # Debugged with examples from https://kavaliro.com/wp-content/uploads/2014/03/AES.pdf
    newData4x4 = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]

    for col in range(4):
        #   a1 = 0x02●b1 ⊕ 0x03●b2 ⊕ 0x01●b3 ⊕ 0x01●b4
        newData4x4[0][col] = MultGF8(0x2, data4x4[0][col]) ^ MultGF8(0x3, data4x4[1][col]) ^ MultGF8(0x1, data4x4[2][col]) ^ MultGF8(0x1, data4x4[3][col])
        #   a2 = 0x01●b1 ⊕ 0x02●b2 ⊕ 0x03●b3 ⊕ 0x01●b4
        newData4x4[1][col] = MultGF8(0x1, data4x4[0][col]) ^ MultGF8(0x2, data4x4[1][col]) ^ MultGF8(0x3, data4x4[2][col]) ^ MultGF8(0x1, data4x4[3][col])
        #   a3 = 0x01●b1 ⊕ 0x01●b2 ⊕ 0x02●b3 ⊕ 0x03●b4
        newData4x4[2][col] = MultGF8(0x1, data4x4[0][col]) ^ MultGF8(0x1, data4x4[1][col]) ^ MultGF8(0x2, data4x4[2][col]) ^ MultGF8(0x3, data4x4[3][col])
        #   a4 = 0x03●b1 ⊕ 0x01●b2 ⊕ 0x01●b3 ⊕ 0x02●b4
        newData4x4[3][col] = MultGF8(0x3, data4x4[0][col]) ^ MultGF8(0x1, data4x4[1][col]) ^ MultGF8(0x1, data4x4[2][col]) ^ MultGF8(0x2, data4x4[3][col])
    
    return newData4x4

def invMixCols(data4x4):
    # Advice found on http://www.herongyang.com/Cryptography/AES-MixColumns-Procedure-Algorithm.html
    # Could not get the galois library to compile so see MultGF2 function above, it is cited.

    newData4x4 = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]

    for col in range(4):
        #   a1 = 0x0e●b1 ⊕ 0x0b●b2 ⊕ 0x0d●b3 ⊕ 0x09●b4
        newData4x4[0][col] = MultGF8(0xe, data4x4[0][col]) ^ MultGF8(0xb, data4x4[1][col]) ^ MultGF8(0xd, data4x4[2][col]) ^ MultGF8(0x9, data4x4[3][col])
        #   a2 = 0x09●b1 ⊕ 0x0e●b2 ⊕ 0x0b●b3 ⊕ 0x0d●b4
        newData4x4[1][col] = MultGF8(0x9, data4x4[0][col]) ^ MultGF8(0xe, data4x4[1][col]) ^ MultGF8(0xb, data4x4[2][col]) ^ MultGF8(0xd, data4x4[3][col])
        #   a3 = 0x0d●b1 ⊕ 0x09●b2 ⊕ 0x0e●b3 ⊕ 0x0b●b4
        newData4x4[2][col] = MultGF8(0xd, data4x4[0][col]) ^ MultGF8(0x9, data4x4[1][col]) ^ MultGF8(0xe, data4x4[2][col]) ^ MultGF8(0xb, data4x4[3][col])
        #   a4 = 0x0b●b1 ⊕ 0x0d●b2 ⊕ 0x09●b3 ⊕ 0x0e●b4
        newData4x4[3][col] = MultGF8(0xb, data4x4[0][col]) ^ MultGF8(0xd, data4x4[1][col]) ^ MultGF8(0x9, data4x4[2][col]) ^ MultGF8(0xe, data4x4[3][col])

    return newData4x4

def Transpose(matrix4x4):
    result = [[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]
    for row in range(4):
        for col in range(4):
            result[col][row] = matrix4x4[row][col]

    return result

def xorData(data1, data2):
    if len(data1) is not len(data2):
        raise "ERROR: Bad sizes cannot xor: " + str(len(data1)) + ", " + str(len(data2))
    for row in range(len(data1)):
        data1[row]= data1[row] ^ data2[row]
    return data1

def RotWord(rowOfBytes):
    # (Recall that the key schedule transposes rows and cols for easier computation)
    return rowOfBytes[1:] + rowOfBytes[:1]

def rcon(i):
    # Rcon table computed by hand (& checked against https://braincoke.fr/blog/2020/08/the-aes-key-schedule-explained/#rcon) 
    # for simplicity to avoid repeated computation
    # Since it is only used for 0..10 rounds, only need it for entries 0 to 10
    rc = [ 0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

    return [rc[i], 0, 0, 0]

def KeySchedule(orig_key):
    # Returns the scheduled key for the nth round
    # With https://en.wikipedia.org/wiki/AES_key_schedule as reference
    # Also from https://www.youtube.com/watch?v=gP4PqVGudtg
    
    # For a AES-128 (implemented here), N = 4 (Key has 4-32-bit-words), R = 11 (key expansion rounds)
    N = 4
    rounds = 11
    W = []
    keys = []

    # Note that for easier implementation, we flip rows and columns here
    flipped_key = Transpose(orig_key)

    for r in range(rounds):
        for i in range(r, r+N):
            # i can be thought of as a column of a large, key-expanded matrix
            if (i < N):
                # If this is one of the first N columns, it stays the same
                W.append(flipped_key[i])
            elif (0 == i % N):
                # If i is a multiple of N, the column undergoes W[i] = W[i-4] + SubWord(RotWord(W[i-1])) + rcon[i/n]
                sub_result = subBytes(RotWord(W[i-1]), Sbox)
                W.append(xorData(W[i-N], xorData(sub_result, rcon(i//N))))
            else:
                # W[i] = W[i-N] + W[i-1]
                W.append(xorData(W[i-1], W[i-N]))
        
        keys.append(Transpose(W[r:r+N]))
    
    return keys

def encrypt(byteArr, key):
    data4x4 = loadInto4x4Bytes(byteArr)
    keys = KeySchedule(loadInto4x4Bytes(key))

    # initial round - xor/AddRoundKey
    data4x4 = addRoundKey(data4x4, keys[0])

    # [N-2] rounds of substitute, shift, mix, add (xor)
    # For this implementation, N = 10
    for i in range(1, 10):
        data4x4 = subBytes(data4x4, Sbox)
        data4x4 = shiftRows(data4x4)
        data4x4 = mixCols(data4x4)
        data4x4 = addRoundKey(data4x4, keys[i])

    # last round has subtract, shift, and add
    data4x4 = subBytes(data4x4, Sbox)
    data4x4 = shiftRows(data4x4)
    data4x4 = addRoundKey(data4x4, keys[10])

    return unload4x4BytesToArr(data4x4)

def unencrypt(byteArr, key):
    data4x4 = loadInto4x4Bytes(byteArr)
    keys = KeySchedule(loadInto4x4Bytes(key))

    # initial round - xor/AddRoundKey
    data4x4 = addRoundKey(data4x4, keys[10])

    # [N-2] rounds of substitute, shift, mix, add (xor)
    # For this implementation, N = 10
    for i in range(9, 0, -1):
        data4x4 = invShiftRows(data4x4)
        data4x4 = subBytes(data4x4, Sbox_inv)
        data4x4 = addRoundKey(data4x4, keys[i])
        data4x4 = invMixCols(data4x4)

    # last round has subtract, shift, and add
    data4x4 = invShiftRows(data4x4)
    data4x4 = subBytes(data4x4, Sbox_inv)
    data4x4 = addRoundKey(data4x4, keys[0])
    return unload4x4BytesToArr(data4x4)

def printbytes(byte_arr, str_descript):
    bytestr = "0x"
    for byte in byte_arr:
        hex_str = hex(byte).upper()[2:]
        if len(hex_str) is 1:
            hex_str = "0" + hex_str
        bytestr+=hex_str + " "
    print(str_descript + ": ", bytestr)

def main():
    # ser = serial.Serial(port = "COM4", baudrate = 9600)

    # Key should be 4 words = 16 Bytes (for AES-128) bytes - this is a very insecure key but shows how the process works
    key = "ComputerNetworks"
    key_arr_bytes = [ord(char) for char in key]
    

    while (True):
        user_in = input("'R' to read, 'W' to write, enter to stop: ")
        if(len(user_in) is 0):
            break
        if(user_in.upper()[0] is "R"):
            serial.send("read")
            ser_bytes = ser.readline()
            response = unencrypt(ser_bytes, key_arr_bytes)
            print("Response is: ", response)
            continue
        elif(user_in.upper()[0] is "W"):
            user_in = input("What to send? Max 16 chars: ")
            input_byte_arr = [ord(char) for char in user_in]
            print(input_byte_arr, type(input_byte_arr))
            to_send = encrypt(input_byte_arr[:16], key_arr_bytes)
            # serial.send(to_send)
            printbytes(input_byte_arr[:16], "Input in bytes")
            printbytes(key_arr_bytes, "Key in bytes")
            printbytes(to_send, "Encrypted in bytes")
            unencrypted = unencrypt(to_send, key_arr_bytes)
            strsent = ""
            for byte in unencrypted:
                strsent+=chr(byte)
            print("DID YOU SEND", strsent)
            continue
        print("Unrecognized input")


def cleanup():
    if ser is not None:
        ser.close()

if __name__ == "__main__":
    # try:
        main()
    # except Exception as e:
    #     print(e)
    # finally:
    #     cleanup()

