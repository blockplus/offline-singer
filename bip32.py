
import sys, ctypes, hmac, hashlib, re
from binascii import hexlify, unhexlify
from Crypto.Hash import SHA512
from Crypto import Random
from base58 import *
from ecdsa_keys import *

class bip32(object):

	def __init__(self, testnet = False, public_prefix = '00', private_prefix = '08'):
		super(bip32, self).__init__()
		self.testnet = testnet
		self.public_prefix = public_prefix
		self.private_prefix = private_prefix

	def generate_master_key(self):

		# Get hex code
		self.digest = SHA512.new(Random.get_random_bytes(1024)).hexdigest();
		prefix = '04358394' if self.testnet == True else '0488ade4'
		hex = prefix + '00' + '00000000' + '00000000' + self.digest[:64] + '00' + self.digest[64:]

		# BASE58 encode + checksum
		master_key = b58encode_checksum(unhexlify(hex));

		# Generate child key
		return self.derive_child(master_key, '0', True)

	def decode_key(self, ext_key):
		decoded = b58decode(ext_key, None)
		self.magic_bytes = decoded[:4]
		self.type = 'private' if hexlify(self.magic_bytes) == '0488ade4' or hexlify(self.magic_bytes) == '04358394' else 'public'
		self.depth = int(hexlify(decoded[4:5]), 10)
		self.fingerprint = decoded[5:9]
		self.i = decoded[9:13]
		self.chain_code = decoded[13:45]
		self.key = decoded[45:78]


	def encode_key(self):
		prefix = unhexlify('00') if self.type == 'private' else ''
		newkey = self.magic_bytes + unhexlify(hexlify(ctypes.c_uint8(self.depth))) + self.fingerprint + self.i + self.chain_code + prefix + self.key
		return b58encode_checksum(newkey);


	def ext_private_to_public(self, ext_key):

		# Decode key
		self.decode_key(ext_key)
		if self.type == 'public':
			return ext_key

		# Get public key
		self.key = self.private_to_public(self.key, True)
		self.magic_bytes = unhexlify('0488b21e') if self.testnet == False else unhexlify('043587cf')
		self.type = 'public'

		# Encode key
		return self.encode_key()


	def private_to_public(self, privkey, compressed = False):

		pubkey = Public_key(g, g * int(hexlify(privkey), 16))
		if compressed == True:
			return unhexlify(('02' if (int(pubkey.point.y() % 2) == 0) else '03') + hex(pubkey.point.x()).rstrip('L').lstrip('0x').zfill(64))
		else:
			return unhexlify('04' + hex(pubkey.point.x()).rstrip('L').lstrip('0x').zfill(64) + hex(pubkey.point.y()).rstrip('L').lstrip('0x').zfill(64))


	def derive_child(self, ext_key, keyindex, hardened = False):

		# Decode key
		self.decode_key(ext_key)
		if self.type == 'private':
			pubkey = self.private_to_public(self.key, True)
		else:
			pubkey = self.key

		# Get keyindex
		keyindexes = keyindex.split("/") if '/' in keyindex else [ keyindex ]
		if len(keyindexes) == 1 and hardened == True:
			n = ctypes.c_uint32(int(keyindexes.pop(0)) + 2147483648)
			pubkey = unhexlify('00') + self.key
		else:
			n = ctypes.c_uint32(int(keyindexes.pop(0)))
		i = unhexlify(hexlify(n))[::-1]

		# Generate new key
		data = pubkey + i
		hash = hmac.new(self.chain_code, data, hashlib.sha512).digest()
		newkey = hex(((int(hexlify(hash[:32]), 16) + int(hexlify(self.key), 16)) % g.order())).lstrip('0x').rstrip('L').zfill(64)

		# Set variables
		self.type = 'private'
		self.key = unhexlify(newkey)
		self.chain_code = hash[32:]
		self.depth += 1
		self.fingerprint = hashlib.new('ripemd160', hashlib.sha256(pubkey).digest()).digest()[:4]
		self.i = i

		# Return
		if len(keyindexes) > 0:
			return self.derive_child(self.encode_key(), '/'.join(keyindexes))
		else:
			return self.encode_key()


	def key_to_address(self, ext_key):

		# Decode key
		self.decode_key(ext_key)
		if self.type == 'private':
			pubkey = self.private_to_public(self.key, True)
		else:
			pubkey = self.key

		# Generate address
		hash = unhexlify(self.public_prefix) + hashlib.new('ripemd160', hashlib.sha256(pubkey).digest()).digest()
		return b58encode_checksum(hash)

	def validate_ext_private_key(self, ext_key):

		# Initial checks
		if ext_key[:4] != 'tprv' and ext_key[:4] != 'xprv':
			return False
		elif len(ext_key) < 100 or len(ext_key) > 130:
			return False

		# Decode key, and check magic bytes
		decoded = hexlify(b58decode(ext_key, None))
		if decoded[:8] != '04358394' and decoded[:8] != '0488ade4':
			return False

		# Import key
		self.decode_key(ext_key)

		# Check key
		if int(hexlify(self.key), 16) == 0 or int(hexlify(self.key), 16) == g.order():
			return False

		# Return
		return True

	def validate_address(self, address):

		# Check length
		decode = b58decode(address, None)
		if len(decode) != 25:
			return False

		# Check address prefix
		prefix = hexlify(decode[:1])
		if prefix != 'c4' and prefix != '05' and prefix != '6f' and prefix != self.public_prefix:
			return False

		# Compare checksum
		hash = hashlib.sha256(hashlib.sha256(decode[:21]).digest()).digest()
		return decode[-4:] == hash[:4]

	def validate_sigscript(self, sig_script, privkeys = [], keyindexes = []):

		# Check if sig script matches
		s = re.match(r'76a914(.+?)88ac$', sig_script, re.M|re.I)
		s2 = re.match(r'(..)(.*)(..)ae$', sig_script, re.M|re.I)
		chk_addrs = []
		reqsigs = 1

		# Standard
		if s:
			addr = b58encode_checksum(unhexlify(self.public_prefix + s.group(1)))
			chk_addrs.append(addr)

		# Multisig
		elif s2:

			p = 0
			sig = unhexlify(s2.group(2))
			reqsigs = (int(s2.group(1)) - 50)
			while True:
				length = int(hexlify(sig[p:(p+1)]), 16)
				pubkey = sig[(p+1):(p+length+1)]
				p += (length + 1)

				hash = unhexlify(self.public_prefix) + hashlib.new('ripemd160', hashlib.sha256(pubkey).digest()).digest()
				chk_addrs.append(b58encode_checksum(hash))
				if p >= len(sig):
					break

		else:
			return False

		# Go through private keys, and look for a match
		valid_privkeys = []
		for chk_addr in chk_addrs:

			ok = False
			for privkey in privkeys:

				for keyindex in keyindexes:
					child_key = self.derive_child(privkey, keyindex)
					if self.key_to_address(child_key) == chk_addr:
						valid_privkeys.append(child_key)
						ok = True
						break

				if ok == True:
					break

		# Return
		if len(valid_privkeys) > 0:
			return reqsigs, valid_privkeys
		else:
			return reqsigs, False



	def sigscript_to_address(self, sigscript):

		# Check if sig script matches
		s = re.match(r'76a914(.+?)88ac$', sigscript, re.M|re.I)
		s2 = re.match(r'(..)(.*)(..)ae$', sigscript, re.M|re.I)
		chk_addrs = []

		# Standard
		if s:
			addr = b58encode_checksum(unhexlify(self.public_prefix + s.group(1)))
			return addr

		# Multisig
		elif s2:
			prefix = 'c4' if self.testnet == True else '05'
			hash = unhexlify(prefix) + hashlib.new('ripemd160', hashlib.sha256(unhexlify(sigscript)).digest()).digest()
			addr = b58encode_checksum(hash)
			return addr

		else:
			return False



