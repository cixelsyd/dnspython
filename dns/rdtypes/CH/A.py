# Copyright (C) Dnspython Contributors, see LICENSE for text of ISC license

# Copyright (C) 2003-2007, 2009-2011 Nominum, Inc.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose with or without fee is hereby granted,
# provided that the above copyright notice and this permission notice
# appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND NOMINUM DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL NOMINUM BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import dns.rdtypes.mxbase
import struct

class A(dns.rdtypes.mxbase.MXBase):

    """A record for Chaosnet"""

    # domain: the domain of the address
    # address: the 16-bit address

    __slots__ = ['domain', 'address']

    def __init__(self, rdclass, rdtype, address, domain):
        super().__init__(rdclass, rdtype, address, domain)
        object.__setattr__(self, 'domain', domain)
        object.__setattr__(self, 'address', address)

    def to_text(self, origin=None, relativize=True, **kw):
        domain = self.domain.choose_relativity(origin, relativize)
        return '%s %o' % (domain, self.address)

    @classmethod
    def from_text(cls, rdclass, rdtype, tok, origin=None, relativize=True,
                  relativize_to=None):
        domain = tok.get_name(origin, relativize, relativize_to)
        address = tok.get_uint16(base=8)
        tok.get_eol()
        return cls(rdclass, rdtype, address, domain)

    def _to_wire(self, file, compress=None, origin=None, canonicalize=False):
        self.domain.to_wire(file, compress, origin, canonicalize)
        pref = struct.pack("!H", self.address)
        file.write(pref)

    @classmethod
    def from_wire(cls, rdclass, rdtype, wire, current, rdlen, origin=None):
        (domain, cused) = dns.name.from_wire(wire[:current + rdlen - 2],
                                             current)
        current += cused
        (address,) = struct.unpack('!H', wire[current:current + 2])
        if cused + 2 != rdlen:
            raise dns.exception.FormError
        if origin is not None:
            domain = domain.relativize(origin)
        return cls(rdclass, rdtype, address, domain)
