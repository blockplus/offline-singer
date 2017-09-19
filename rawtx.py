
import sys, ctypes, random, re, ecdsa, pprint
from binascii import hexlify, unhexlify
from Crypto.Hash import SHA512
from Crypto import Random
from ecdsa import SigningKey, SECP256k1
from base58 import *
from bip32 import *

class rawtx(object):

	def __init__(self):
		super(rawtx, self).__init__()
		self.version = 1
		self.timelock = unhexlify('00000000')
		self.inputs = []
		self.outputs = []

	def validate_amount(self, amount):

		try:
			amount = float(amount)
		except:
			return False

		if float(amount) < 0.00005430:
			print "No float"
			return False

		return True

	def decode_transaction(self, hexcode):

		# Begin decoding
		try:
			trans = unhexlify(str(hexcode))
		except:
			return False

		# Set initial variables
		self.version = int(hexlify(trans[:4][::-1]), 10)
		num_inputs = int(hexlify(trans[4:5]), 10)
		p = 5

		# Go through inputs
		for x in range(0, num_inputs):
			txid = trans[p:(p+32)][::-1]
			vout = int(hexlify(trans[(p+32):(p+36)][::-1]))
			script_length, blen = self.decode_vint(trans, (p + 36))
			p += blen

			sigscript = trans[(p+37):(p+37+script_length)]
			p += (41 + script_length);
			sequence = trans[(p-4):p]

			self.inputs.append({
				'txid': txid, 
				'vout': vout, 
				'sigscript': sigscript, 
				'sequence': sequence
			})

		# Go through outputs
		num_outputs = int(hexlify(trans[p:(p+1)]), 10)
		p += 1
		for x in range (0, num_outputs):
			amount = int(hexlify(trans[p:(p+8)][::-1]), 16) / 1e8
			script_length = int(hexlify(trans[(p+8):(p+9)]), 16)
			script = trans[(p+9):(p+9+script_length)]
			p += (9 + script_length)

			self.outputs.append({
				'amount': amount, 
				'script': script
			})

		# Finish up
		self.timelock = trans[p:(p+4)]

	def encode_transaction(self, input_num = None):

		# Start transaction
		trans = bytearray()
		trans += ctypes.c_uint32(self.version)
		trans += ctypes.c_uint8(len(self.inputs))

		# Go through inputs
		x=0
		for item in self.inputs:
			trans += item['txid'][::-1]
			trans += ctypes.c_uint32(item['vout'])

			if input_num == None or input_num == x:
				trans += self.encode_vint(len(item['sigscript']))
				trans += item['sigscript']
			else:
				trans += unhexlify('00')

			trans += item['sequence']
			x += 1

		# Go through outputs
		trans += ctypes.c_uint8(len(self.outputs))
		for item in self.outputs:

			# Add output
			trans += ctypes.c_uint64(int(item['amount'] * 1e8))
			trans += self.encode_vint(len(item['script']))
			trans += item['script']

		# Finish encoding
		trans += self.timelock
		return trans

	def add_input(self, txid, vout, sigscript, keyindex = None, privkeys = None, sequence = None):
		if sequence == None:
			sequence = unhexlify('ffffffff')

		if type(keyindex) == str or type(keyindex) == unicode:
			keyindexes = [keyindex]
		elif type(keyindex) == list:
			keyindexes = keyindex
		else:
			print "Invalid keyindex for input"
			return False

		self.inputs.append({
			'txid': txid, 
			'vout': vout, 
			'keyindex': keyindexes, 
			'sigscript': sigscript, 
			'sequence': sequence, 
			'privkeys': privkeys
		})

	def add_output(self, amount, address):

		# Create script
		daddr = hexlify(b58decode(address, None))
		if daddr[:2] == 'c4' or daddr[:2] == '05':
			script = 'a914' + daddr[2:42] + '87'
		else:
			script = '76a914' + daddr[2:42] + '88ac'
		
		# Add output
		self.outputs.append({
			'amount': amount, 
			'script': unhexlify(script)
		})

	def get_vint(self, trans, p):

		if (trans[p] == 0xfd):
			print("FD")
		elif (trans[p] == 0xfe):
			print("FE")
		elif (trans[p] == 0xff):
			print("FF")
		else:
			print("VNONE")


	def set_keyindex(self, x, keyindex, private_key):
		bip = bip32()
		address = bip.key_to_address(bip.derive_child(private_key, str(keyindex)))

		self.inputs[x]['keyindex'] = str(keyindex)
		self.inputs[x]['sigscript'] = unhexlify('76a914' + hexlify(b58decode(address, None))[2:] + '88ac')

	def sign_transaction(self):

		# Go through inputs
		x = 0
		fully_signed = True
		for item in self.inputs:
			hexcode = self.encode_transaction(x) + unhexlify('01000000')

			# Get pub keys from sigscript
			pubkeys = []
			s = re.match(r'(..)(.*)(..)ae$', hexlify(item['sigscript']), re.M|re.I)
			if s:
				p = 0
				sig = unhexlify(s.group(2))
				reqsigs = (int(s.group(1)) - 50)

				while True:
					length = int(hexlify(sig[p:(p+1)]), 16)
					pubkeys.append(sig[(p+1):(p+length+1)])
					p += (length + 1)
					if p >= len(sig):
						break

			else:
				pubkeys.append(item['sigscript'])
				reqsigs = 1

			# Go through private keys, and get signatures
			self.inputs[x]['signatures'] = []
			for privkey in item['privkeys']:

				# Decode child key
				bip = bip32()
				bip.decode_key(privkey)
				public_key = bip.private_to_public(bip.key, True)
				uncompressed_public_key = bip.private_to_public(bip.key)

				# Go through public keys
				for pkey in pubkeys:

					# Check public key
					if pkey != public_key and pkey != uncompressed_public_key and pkey != item['sigscript']:
						continue

					# Get hash
					hash = hashlib.sha256(hashlib.sha256(hexcode).digest()).digest()

					# Sign transaction
					signingkey = ecdsa.SigningKey.from_string(bip.key[1:], curve=ecdsa.SECP256k1)
					der = signingkey.sign_digest(hash, sigencode=ecdsa.util.sigencode_der) + unhexlify('01')
					der = self.verify_der(der)
					self.inputs[x]['signatures'].append(der)

			# Check # of signatures
			if len(self.inputs[x]['signatures']) >= reqsigs:

				# Create sig
				if len(self.inputs[x]['signatures']) > 1:					
					full_sig = unhexlify("00")
					for sign in self.inputs[x]['signatures']:
						full_sig += self.encode_vint(len(sign)) + sign

					self.inputs[x]['sigscript'] = full_sig + unhexlify('4c') + self.encode_vint(len(item['sigscript'])) + item['sigscript']

				else:
					self.inputs[x]['sigscript'] = self.encode_vint(len(self.inputs[x]['signatures'][0])) + self.inputs[x]['signatures'][0]
					self.inputs[x]['sigscript'] += self.encode_vint(len(public_key)) + public_key

			# Partial signatures
			else:
				fully_signed = False

			x += 1

		# Done foreach loop here
		if fully_signed == True:
			return hexlify(self.encode_transaction())
		else:
			return False


	def verify_der(self, der):

		# Decode der signature
		code = der
		r_length = int(hexlify(code[3]), 16)
		s_length = int(hexlify(code[(5 + r_length)]), 16)

		# Get r / s values
		r = hexlify(code[4:(4 + r_length)])
		s = hexlify(code[(6 + r_length):(6 + r_length + s_length)])

		# Check if high S value
		if (int(s, 16) > int('7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5D576E7357A4501DDFE92F46681B20A0', 16)):
			new_s = format(int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16) - int(s, 16), 'x')
			new_s_length = len(new_s) / 2
			new_der_length = r_length + new_s_length + 4;
			der = '30' + hexlify(ctypes.c_uint8(new_der_length)) + '02' + hexlify(ctypes.c_uint8(r_length)) + r +  '02' + hexlify(ctypes.c_uint8(new_s_length)) + new_s + '01'
			der = unhexlify(der)

		# Return
		return der


	def encode_vint(self, num):

		## Get vint
		if num < 253:
			res = hexlify(ctypes.c_uint8(num))
		elif num < 65535:
			res = 'fd' + hexlify(ctypes.c_uint16(num))
		elif num < 4294967295:
			res = 'fe' + hexlify(ctypes.c_uint32(num))
		else:
			res = 'ff' + hexlify(ctypes.c_uint64(num))

		# Return
		return unhexlify(res)

	def decode_vint(self, trans, s):

		if hexlify(trans[s:(s+1)]) == 'ff':
			num = int(hexlify(trans[(s+1):(s+5)][::-1]), 16)
			blen = 5
		elif hexlify(trans[s:(s+1)]) == 'fe':
			num = int(hexlify(trans[(s+1):(s+3)][::-1]), 16)
			blen = 3
		elif hexlify(trans[s:(s+1)]) == 'fd':
			num = int(hexlify(trans[(s+1):(s+2)][::-1]), 16)
			blen = 2
		else:
			num = int(hexlify(trans[s:(s+1)]), 16)
			blen = 0

		# Return
		return num, blen







