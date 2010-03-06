# encoding: UTF-8
from ff import GF256int
from polynomial import Polynomial

"""This module implements Reed-Solomon Encoding.
Specifically, RS(255,223), 223 data bytes and 32 parity bytes

Warning: Because of the way I've implemented things, leading null bytes in a
message are dropped. Be careful if encoding binary data.
"""

n = 255
k = 223

# Generate the generator polynomial for RS codes
# g(x) = (x-α^0)(x-α^1)...(x-α^254)
# α is 3, a generator for GF(2^8)
g = Polynomial((GF256int(1),))
for alpha in xrange(1,n-k+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    g = g * p


h = Polynomial((GF256int(1),))
for alpha in xrange(n-k+1,n+1):
    p = Polynomial((GF256int(1), GF256int(3)**alpha))
    h = h * p

# g*h is used in verification, and is always x^255+1 when n=255
gtimesh = Polynomial(x255=GF256int(1), x0=GF256int(1))

def encode(message, poly=False):
    """Encode a given string with reed-solomon encoding. Returns a byte
    string with 32 parity bytes at the end.
    If poly is not False, returns the encoded Polynomial object instead of
    the polynomial translated back to a string
    """
    if len(message)>k:
        raise ValueError("Message length is max %d. Message was %d" % (k,
            len(message)))

    # Encode message as a polynomial:
    m = Polynomial(GF256int(ord(x)) for x in message)

    # Shift polynomial up by n-k (32) by multiplying by x^32
    mprime = m * Polynomial((GF256int(1),) + (GF256int(0),)*(n-k))

    # mprime = q*g + b for some q
    # so let's find b:
    b = mprime % g

    # Subtract out b, so now c = q*g
    c = mprime - b
    # Since c is a multiple of g, it has (at least) n-k roots: α^1 through
    # α^(n-k)

    if poly:
        return c

    # Turn the polynomial c back into a byte string
    return "".join(chr(x) for x in c.coefficients)

def verify(code):
    """Verifies the code is valid by testing that the code as a polynomial code
    divides g
    returns True/False
    """
    c = Polynomial(GF256int(ord(x)) for x in code)
    # Not sure what I was thinking with this, it still works...
    #return (c*h)%gtimesh == Polynomial((0,))

    # ...But since all codewords are multiples of g, checking that code divides
    # g should suffice for validating a codeword.
    return c % g == Polynomial((0,))

def decode(r):
    """Given a received byte string r, attempts to decode it. If it's a valid
    codeword, or if there are less than 2s errors, the message is returned
    """
    if verify(r):
        # The last 32 bytes are parity
        return r[:-32]

    # Turn r into a polynomial
    r = Polynomial(GF256int(ord(x)) for x in r)

    # Compute the syndromes:
    sz = _syndromes(r)

    # Find the error locator polynomial and error evaluator polynomial using
    # the Berlekamp-Massey algorithm
    sigma, omega = _berlekamp_massey()

    # Now use Chien's procedure to find the error locations
    X = _chien_search(sigma)

    # And finally, find the error magnitudes with Forney's Formula
    Y = _forney(omega, X)

    # Put the error and locations together to form the error polynomial
    # TODO

    # And we get our real codeword!
    c = r - E

    # Form it back into a string and return all but the last 32 bytes
    return "".join(chr(x) for x in c.coefficients)[:-32]


def _syndromes(r):
    """Given the received codeword r in the form of a Polynomial object,
    computes the syndromes and returns the syndrome polynomial
    """
    # s[l] is the received codeword evaluated at α^l for 1 <= l <= s
    # α in this implementation is 3
    s = [GF256int(0)] # s[0] is not defined
    for l in xrange(1, n-k+1):
        s.append( r.evaluate( GF256int(3)**l ) )

    # Now build a polynomial out of all our s[l] values
    # s(z) = sum(s_i * z^i, i=1..inf)
    sz = Polynomial( reversed( s ) )

    return sz

def _berlekamp_massey(s):
    """Computes and returns the error locator polynomial (sigma) and the error
    evaluator polynomial (omega)
    The parameter s is the syndrome polynomial (syndromes encoded in a
    generator function)
    """
    # Initialize
    sigma =  [ Polynomial((GF256int(1),)) ]
    omega =  [ Polynomial((GF256int(1),)) ]
    tao =    [ Polynomial((GF256int(1),)) ]
    gamma =  [ Polynomial((GF256int(1),)) ]
    D =      [ GF256int(0) ]
    B =      [ GF256int(0) ]
    
    # TODO

    return sigma[-1], omega[-1]

def _chien_search(sigma):
    pass # TODO

def _forney(omega, X):
    pass # TODO
