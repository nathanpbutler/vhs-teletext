# * Copyright 2016 Alistair Buxton <a.j.buxton@gmail.com>
# *
# * License: This program is free software; you can redistribute it and/or
# * modify it under the terms of the GNU General Public License as published
# * by the Free Software Foundation; either version 3 of the License, or (at
# * your option) any later version. This program is distributed in the hope
# * that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# * warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# * GNU General Public License for more details.


"""Byte coding and error protection

Odd parity:
The high bit of each byte is set such that there are an odd number of bits in the byte.
Single bit errors can be detected.

Hamming 8/4:
P1 D1 P2 D2 P3 D3 P4 D4 (Transmission order, LSB first.)
Single bit errors can be identified and corrected. Double bit errors can be detected.

Hamming 24/16:
P1 P2 D1 P3 D2 D3 D4 P4  D5 D6 D7 D8 D9 D10 D11 P5  D12 D13 D14 D15 D16 D17 D18 P6
Single bit errors can be identified and corrected. Double bit errors
can be detected.

"""
import numpy as np


def thue_morse(n, even=True):
    arr = np.array([even], dtype=np.bool)
    for i in range(0, n):
        arr = np.append(arr,~arr)
    return arr

# hamming 8/4 encoding look up table
hamming8_enc = np.array([
    0x15, 0x02, 0x49, 0x5e, 0x64, 0x73, 0x38, 0x2f, 0xd0, 0xc7, 0x8c, 0x9b, 0xa1, 0xb6, 0xfd, 0xea,
], dtype=np.uint8)
hamming8_enc.flags.writeable = False

# hamming 8/4 correctable errors occur when the input has even parity
hamming8_cor = thue_morse(8, even=True)
hamming8_cor.flags.writeable = False

# hamming 8/4 uncorrectable errors always have odd parity,
# but so do valid bytes.
hamming8_unc = thue_morse(8, even=False)
hamming8_unc[hamming8_enc] = False
hamming8_unc.flags.writeable = False

# hamming 8/4 decoding lookup table
hamming8_dec = np.array([
    0x1, 0xf, 0x1, 0x1, 0xf, 0x0, 0x1, 0xf, 0xf, 0x2, 0x1, 0xf, 0xa, 0xf, 0xf, 0x7,
    0xf, 0x0, 0x1, 0xf, 0x0, 0x0, 0xf, 0x0, 0x6, 0xf, 0xf, 0xb, 0xf, 0x0, 0x3, 0xf,
    0xf, 0xc, 0x1, 0xf, 0x4, 0xf, 0xf, 0x7, 0x6, 0xf, 0xf, 0x7, 0xf, 0x7, 0x7, 0x7,
    0x6, 0xf, 0xf, 0x5, 0xf, 0x0, 0xd, 0xf, 0x6, 0x6, 0x6, 0xf, 0x6, 0xf, 0xf, 0x7,
    0xf, 0x2, 0x1, 0xf, 0x4, 0xf, 0xf, 0x9, 0x2, 0x2, 0xf, 0x2, 0xf, 0x2, 0x3, 0xf,
    0x8, 0xf, 0xf, 0x5, 0xf, 0x0, 0x3, 0xf, 0xf, 0x2, 0x3, 0xf, 0x3, 0xf, 0x3, 0x3,
    0x4, 0xf, 0xf, 0x5, 0x4, 0x4, 0x4, 0xf, 0xf, 0x2, 0xf, 0xf, 0x4, 0xf, 0xf, 0x7,
    0xf, 0x5, 0x5, 0x5, 0x4, 0xf, 0xf, 0x5, 0x6, 0xf, 0xf, 0x5, 0xf, 0xe, 0x3, 0xf,
    0xf, 0xc, 0x1, 0xf, 0xa, 0xf, 0xf, 0x9, 0xa, 0xf, 0xf, 0xb, 0xa, 0xa, 0xa, 0xf,
    0x8, 0xf, 0xf, 0xb, 0xf, 0x0, 0xd, 0xf, 0xf, 0xb, 0xb, 0xb, 0xa, 0xf, 0xf, 0xb,
    0xc, 0xc, 0xf, 0xc, 0xf, 0xc, 0xd, 0xf, 0xf, 0xc, 0xf, 0xf, 0xa, 0xf, 0xf, 0x7,
    0xf, 0xc, 0xd, 0xf, 0xd, 0xf, 0xd, 0xd, 0x6, 0xf, 0xf, 0xb, 0xf, 0xe, 0xd, 0xf,
    0x8, 0xf, 0xf, 0x9, 0xf, 0x9, 0x9, 0x9, 0xf, 0x2, 0xf, 0xf, 0xa, 0xf, 0xf, 0x9,
    0x8, 0x8, 0x8, 0xf, 0x8, 0xf, 0xf, 0x9, 0x8, 0xf, 0xf, 0xb, 0xf, 0xe, 0x3, 0xf,
    0xf, 0xc, 0xf, 0xf, 0x4, 0xf, 0xf, 0x9, 0xf, 0xf, 0xf, 0xf, 0xf, 0xe, 0xf, 0xf,
    0x8, 0xf, 0xf, 0x5, 0xf, 0xe, 0xd, 0xf, 0xf, 0xe, 0xf, 0xf, 0xe, 0xe, 0xf, 0xe,
], dtype=np.uint8)
hamming8_dec.flags.writeable = False

# odd parity bits
parity_tab = thue_morse(7, even=True) * 0x80
parity_tab.flags.writeable = False


def hamming8_encode(a):
    return hamming8_enc[a]


def hamming8_decode(a):
    return hamming8_dec[a]


def hamming16_encode(a):
    return np.ravel(np.column_stack((
        hamming8_enc[a & 0xf],
        hamming8_enc[a >> 4],
    )))


def hamming16_decode(a):
    if len(a) == 2:
        return hamming8_dec[a[0]] | (hamming8_dec[a[1]] << 4)
    else:
        return hamming8_dec[a[0::2]] | (hamming8_dec[a[1::2]] << 4)


def hamming8_correctable_errors(a):
    return hamming8_cor[a]


def hamming8_uncorrectable_errors(a):
    return hamming8_unc[a]


def hamming8_errors(a):
    return (2 * hamming8_unc[a]) + hamming8_cor[a]


def parity_encode(a):
    return a | parity_tab[a]


def parity_decode(a):
    return a & 0x7f


def parity_errors(a):
    return parity_tab[a&0x7f] != a&0x80


def bcd8_decode(a):
    return ((a>>4)*10) + (a&0xf) - 11


def bcd8_encode(a):
    return ((a/10)<<4) + (a%10) + 11
