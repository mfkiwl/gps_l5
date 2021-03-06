#!/usr/bin/python3

import numpy as np
import scipy

# PRN #s 1-37
# 38+ use a different generation method (?)
PRN_TAPS = [
    None, # No PRN 0
    [2, 6],
    [3, 7],
    [4, 8],
    [5, 9],
    [1, 9],
    [2, 10],
    [1, 8],
    [2, 9],
    [3, 10],
    [2, 3],
    [3, 4],
    [5, 6],
    [6, 7],
    [7, 8],
    [8, 9],
    [9, 10],
    [1, 4],
    [2, 5],
    [3, 6],
    [4, 7],
    [5, 8],
    [6, 9],
    [1, 3],
    [4, 6],
    [5, 7],
    [6, 8],
    [7, 9],
    [8, 10],
    [1, 6],
    [2, 7],
    [3, 8],
    [4, 9],
    [5, 10], # PRN 33 - Reserved
    [4, 10], # PRN 34 - Identical to 37
    [1, 7],
    [2, 8],
    [4, 10], # PRN 37 - Identical to 34
]

CODE = []

# Calculate num_bits of a n-bit LFSR with given taps & initial value
# Tap order mimics IS-GPS presentation (bit 1 is on the left, 13 on the right)
def gen_lfsr_code(n, taps, output_tap = 13, initial = 1, num_bits = 1):

    # Truncate register to n bits
    reg = initial & (2**n-1)

    # Output - array of 1, 0
    out = []

    for i in range(num_bits):
        out.append((reg >> (n - output_tap)) & 1)
        feedback = 0

        # Apply taps
        for tap in taps:
            feedback ^= (reg >> (n - tap)) & 1 

        reg = (reg >> 1) | (feedback << (n-1))

    return(np.array(out))

# Generate 1023-bit PRN code for a given PRN#
def get_code(prn):
    
#    G21 = do_shift_reg([10, 9, 8, 6, 3, 2], output_tap=PRN_TAPS[prn][0])
#    G22 = do_shift_reg([10, 9, 8, 6, 3, 2], output_tap=PRN_TAPS[prn][1])
#    G1  = do_shift_reg([10, 3])

    G21 = gen_lfsr_code(10, [10, 9, 8, 6, 3, 2], PRN_TAPS[prn][0], initial=1023, num_bits=1023) 
    G22 = gen_lfsr_code(10, [10, 9, 8, 6, 3, 2], PRN_TAPS[prn][1], initial=1023, num_bits=1023)
    G1  = gen_lfsr_code(10, [10, 3],             10,               initial=1023, num_bits=1023)

    Gi = np.bitwise_xor(G21, G22)
    out = np.bitwise_xor(G1, Gi)

    return out

# Pre generate codes on import

CODE.append(None)

for i in range(37):
    prn = i+1
    code = get_code(prn)
    CODE.append(code)


# Test
if __name__ == '__main__':
    
    print('')
    print('L1 C/A Code Gen Test (compare to ICD Table 3-1A, pg. 6)')
    print('')
    print('PRN\tFirst Chips (octal)')
    print('')

    for i in range(37):
        prn = i+1
        code = CODE[prn]

        first_ten = code[:10]
        as_bytes = np.packbits(first_ten)
        packed = ((as_bytes[0] << 8) | as_bytes[1]) >> 6

        print('{:2d}\t{:o}'.format(prn, packed))

