import base64

global ENCODING_KEY
ENCODING_KEY = 'd67afc830dab717fd163bfcb0b8b88423e9a1a3b'

def _encode(name, key):
    s = [];
    for i in range(len(name)):
        s.append(chr(ord(name[i]) ^ ord(key[i % len(key)])))
    return s

def _decode(name, key):
    s = []
    for i in range(len(name)):
        s.append(chr(name[i] ^ key[i % len(key)]))
    return s

def obfuscate(name):
    if name is None:
        return ''
    return base64.b64encode(''.join(_encode(name, ENCODING_KEY)).encode())

def deobfuscate(name):
    if name is None:
        return ''
    return ''.join(_decode(base64.b64decode(bytes(name, 'ascii')), bytes(ENCODING_KEY, 'utf-8')))
