
import sys, json, os.path
from binascii import hexlify, unhexlify
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from bip32 import *
from rawtx import *
from import_tx_results import *
from sign_single_tx2 import *

class import_tx(QWidget):

	def __init__(self, parent):
		super(import_tx, self).__init__()
		self.parent = parent
		self.import_tx_layout_num = 2
		self.json = None

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Select file button
		self.lblImportFilename = QLabel(self.tr('No File'))
		self.buttonSelectJSONFile = QPushButton(self.tr('Select File...'))
		self.buttonSelectJSONFile.setMaximumWidth(150)
		self.buttonSelectJSONFile.clicked.connect(self.select_json_file)

		# Textboxes
		txtImportPrivKey = BIP32TextBox()
		self.txtPrivKeys = [ txtImportPrivKey ]

		# Group box for private keys
		self.boxPrivKeys = QGroupBox()
		self.boxPrivKeysLayout = QGridLayout()
		self.boxPrivKeys.setStyleSheet("QGroupBox { margin: 0px; }")
		self.boxPrivKeysLayout.addWidget(QLabel(self.tr('JSON File:  ')), 0, 0, Qt.AlignTop)
		self.boxPrivKeysLayout.addWidget(self.lblImportFilename, 0, 1, Qt.AlignLeft)
		self.boxPrivKeysLayout.addWidget(self.buttonSelectJSONFile, 0, 2, Qt.AlignLeft)
		self.boxPrivKeysLayout.addWidget(QLabel(self.tr('BIP32 Private Key:  ')), 1, 0, Qt.AlignTop)
		self.boxPrivKeysLayout.addWidget(txtImportPrivKey, 1, 1, 1, 2, Qt.AlignTop)
		self.boxPrivKeys.setLayout(self.boxPrivKeysLayout)

		# Add private key link
		lblAddPrivateKey = LinkedLabel(self.tr('Add Private Key...'))
		lblAddPrivateKey.mousePressEvent = self.add_private_key

		# Push button
		self.buttonImportTxs = QPushButton(self.tr('Import Transactions'), self)
		self.buttonImportTxs.setMaximumWidth(250)
		self.buttonImportTxs.clicked.connect(self.ok)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Import Transactions'), 0, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(DescriptionLabel('You may import a JSON file of raw transactions, and have them automatically signed by selecting the file below and entering your BIP32 private key.  You will receive a new JSON file in return, which you must upload to your online system to complete the sends.<br><br><b>NOTE:</b> If these are multisig transactions, and you hold all private keys necessary, you may input more than one private key below.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(self.boxPrivKeys, 2, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(lblAddPrivateKey, 3, 1, 1, 1, Qt.AlignRight)
		layout.addWidget(self.buttonImportTxs, 4, 1, 1, 1, Qt.AlignRight)


	def select_json_file(self, event):
		filename = QFileDialog.getOpenFileName(self, "Open Transaction File", "", "JSON files (*.*)")
		self.lblImportFilename.setText(filename)

	def add_private_key(self, event):

		# Textboxes
		txtPrivKey = BIP32TextBox()
		self.txtPrivKeys.append(txtPrivKey)

		self.boxPrivKeysLayout.addWidget(QLabel('BIP32 Private Key ' + str(self.import_tx_layout_num) + ':  '), self.import_tx_layout_num, 0, Qt.AlignTop)
		self.boxPrivKeysLayout.addWidget(txtPrivKey, self.import_tx_layout_num, 1, 1, 2, Qt.AlignTop)
		self.import_tx_layout_num += 1

	def ok(self):

		# Initialize
		b32 = bip32()

		# Initial checks
		if self.lblImportFilename.text() == '' or not os.path.isfile(self.lblImportFilename.text()):
			QMessageBox.critical(self, "Error", "You did not specify a valid JSON file.  Please ensure you select a JSON file, and try again.")
			return

		# Get JSON code
		fh = open(self.lblImportFilename.text(), 'r')
		try:
			self.json = json.load(fh)
		except:
			QMessageBox.critical(self, "Error", "Unable to load JSON file.  Please ensure the JSON file is correctly formatted, and try again.")
			return
		fh.close()

		# Check BIP32 public / private key index
		if 'public_prefix' in self.json:
			b32.public_prefix = self.json['public_prefix']
		if 'private_prefix' in self.json:
			b32.private_prefix = self.json['private_prefix']

		# Validate private keys
		privkeys = []
		for txt in self.txtPrivKeys:
			if str(txt.toPlainText()) == '':
				continue
			if b32.validate_ext_private_key(str(txt.toPlainText())) == False:
				QMessageBox.critical(self, "Error", "You did not specify a valid BIP32 private key.  Please double check, and try again.")
				return
			privkeys.append(str(txt.toPlainText()))

		# Validate JSON file
		self.validate_json_file(privkeys)
		if len(self.json_errors) > 0:
			QMessageBox.critical(self, "Error", "One or more errors were found within your JSON file.  You may download a JSON file detailing the errors if desired.")
			save_filename = QFileDialog.getSaveFileName(self, "Save Errors File", "errors.json", "JSON files (*.*)")
			if save_filename != '':
				with open(save_filename, 'w') as outfile:
					json.dump(self.json_errors, outfile)
			return

		# Set variables
		txfee = 0.0001 if not 'txfee' in self.json else float(self.json['txfee'])
		txfee_paidby = 'sender' if not 'txfee_paidby' in self.json else self.json['txfee_paidby']
		results = {'tx': [], 'spent_inputs': [], 'change_inputs': [], 'partial_signatures': [] }
		if 'wallet_id' in self.json:
			results['wallet_id'] = self.json['wallet_id']

		# Initialize
		testnet = True if 'testnet' in self.json and self.json['testnet'] == 1 else False
		b32 = bip32(testnet)

		# Go through outputs
		change_id = 0
		if 'outputs' in self.json:

			for out in self.json['outputs']:
			
				# Initialize
				tx = rawtx()
				tx.__init__()

				# Blank variables
				input_amount = 0
				output_amount = 0
				has_change = False
				change_input = { }

				# Add outputs, as needed
				if 'recipients' in out:

					for recip in out['recipients']:
						send_amount = float(recip['amount']) if not txfee_paidby == 'recipient' else float(recip['amount']) - txfee
						tx.add_output(send_amount, recip['address'])
						output_amount += send_amount

				else:
					output_amount = float(out['amount']) if not txfee_paidby == 'recipient' else float(out['amount']) - txfee
					tx.add_output(output_amount, out['address'])


				# Gather inputs for tx
				while len(self.json['inputs']) > 0:
					item = self.json['inputs'].pop(0)
					tx.add_input(unhexlify(item['txid']), int(item['vout']), unhexlify(item['sigscript']), item['keyindex'], item['privkeys'])
					input_amount += float(item['amount'])

					# Mark input spent
					results['spent_inputs'].append(item)

					# Check for change transaction
					if input_amount >= float(output_amount) + txfee:
						change_amount = float(input_amount) - float(output_amount)
						if txfee_paidby == 'sender':
							change_amount -= txfee
						if float(0) >= float(change_amount):
							break

						# Get change key index
						if 'change_keyindex' in out and 'change_sigscript' in out:
							change_keyindex = out['change_keyindex']
							change_sigscript = out['change_sigscript']
						elif 'change_keyindex' in self.json and 'change_sigscript' in self.json:
							change_keyindex = self.json['change_keyindex']
							change_sigscript = self.json['change_sigscript']
						else:
							change_keyindex = item['keyindex']
							change_sigscript = item['sigscript']

						# Get change address
						change_address = b32.sigscript_to_address(change_sigscript)
						tx.add_output(change_amount, change_address)

						# Add change input to results
						has_change = True
						change_id += 1
						change_input['input_id'] = 'c' + str(change_id)
						change_input['vout'] = 1
						change_input['amount'] = change_amount
						change_input['address'] = change_address
						change_input['keyindex'] = change_keyindex
						change_input['sigscript'] = change_sigscript

						if change_sigscript == item['sigscript']:
							change_input['privkeys'] = item['privkeys']
							change_input['reqsigs'] = item['reqsigs']
						else:
							reqsigs, valid_privkeys = b32.validate_sigscript(change_sigscript, privkeys, change_keyindex)
							change_input['privkeys'] = valid_privkeys
							change_input['reqsigs'] = reqsigs

						break

				# Sign transaction
				trans = tx.sign_transaction()
				if trans == False:

					for item in tx.inputs:
						for sig in item['signatures']:
							results['partial_signatures'].append({'input_id': item['input_id'], 'signature': sig})

				else:

					# Add to results
					txid = hexlify(hashlib.sha256(hashlib.sha256(unhexlify(trans)).digest()).digest()[::-1])
					output_id = 0 if not 'output_id' in out else out['output_id']
					tx_results = {
						'output_id': str(output_id), 
						'txid': txid, 
						'amount': output_amount, 
						'input_amount': input_amount, 
						'to_address': out['recipients'], 
						'change_amount': change_amount, 
						'change_address': change_address, 
						'hexcode': trans
					}
					results['tx'].append(tx_results)

					# Add change input, if needed
					if has_change == True:
						change_input['txid'] = txid
						results['change_inputs'].append(change_input)
						self.json['inputs'].append(change_input)

		# Remove excess elements from inputs
		for item in results['spent_inputs']:
			if 'privkeys' in item:
				del item['privkeys']
			if 'reqsigs' in item:
				del item['reqsigs']

		for item in results['change_inputs']:
			if 'privkeys' in item:
				del item['privkeys']
			if 'reqsigs' in item:
				del item['reqsigs']

		# Show results
		w = import_tx_results()
		w.populate_results(results)
		self.parent.stack.addWidget(w)
		self.parent.stack.setCurrentWidget(w)


	def validate_json_file(self, privkeys = []):

		# Initialize
		self.json_errors = []
		b32 = bip32()

		# Check BIP32 public / private key index
		if 'public_prefix' in self.json:
			b32.public_prefix = self.json['public_prefix']
		if 'private_prefix' in self.json:
			b32.private_prefix = self.json['private_prefix']

		# Init a transaction
		tx = rawtx()
		tx.__init__()

		# Go through outputs
		for out in self.json['outputs']:

			if 'recipients' in out:

				for r in out['recipients']:
					if 'amount' not in r:
						self.add_json_error('no_variable', 'output', out['output_id'], 'amount')
					elif 'address' not in r:
						self.add_json_error('no_variable', 'output', out['output_id'], 'address')
					elif tx.validate_amount(r['amount']) == False:
						self.add_json_error('invalid_amount', 'output', out['output_id'], r['amount'])
					elif b32.validate_address(r['address']) == False:
						self.add_json_error('invalid_address', 'output', out['output_id'], r['address'])

			elif 'amount' not in out:
				self.add_json_error('no_variable', 'output', out['output_id'], 'amount')
			elif 'address' not in out:
				self.add_json_error('no_variable', 'output', out['output_id'], 'address')
			elif tx.validate_amount(out['amount']) == False:
				self.add_json_error('invalid_amount', 'output', out['output_id'], out['amount'])
			elif b32.validate_address(out['address']) == False:
				self.add_json_error('invalid_address', 'output', out['output_id'], out['address'])


		# Go through inputs
		x = 0
		for item in self.json['inputs']:

			if 'amount' not in item:
				self.add_json_error('no_variable', 'input', item['input_id'], 'amount')
			elif 'txid' not in item:
				self.add_json_error('no_variable', 'input', item['input_id'], 'txid')
			elif 'vout' not in item:
				self.add_json_error('no_variable', 'input', item['input_id'], 'vout')
			elif 'sigscript' not in item:
				self.add_json_error('no_variable', 'input', item['input_id'], 'sigscript')
			elif 'keyindex' not in item:
				self.add_json_error('no_variable', 'input', item['input_id'], 'keyindex')
			elif tx.validate_amount(item['amount']) == False:
				self.add_json_error('invalid_amount', 'input', item['input_id'], item['amount'])

			# Validate vout
			try:
				int(item['vout'])
			except:
				self.add_json_error('invalid_vout', 'input', item['input_id'], input['vout'])

			# Get keyindexes
			if type(item['keyindex']) == str or type(item['keyindex']) == unicode:
				keyindexes = [item['keyindex']]
			elif type(item['keyindex']) == list:
				keyindexes = item['keyindex']
			else:
				self.add_json_error('invalid_keyindex', 'input', item['input_id'], item['keyindex'])

			# Validate sigscript
			reqsigs, valid_privkeys = b32.validate_sigscript(item['sigscript'], privkeys, keyindexes)
			if valid_privkeys == False:
				self.add_json_error('invalid_sigscript', 'input', item['input_id'], item['sigscript'])
			else:
				self.json['inputs'][x]['privkeys'] = valid_privkeys
				self.json['inputs'][x]['reqsigs'] = reqsigs

			x += 1


	def add_json_error(self, err_code, element_type = 'input', index_id = 0, details = ''):

		# Get message
		if err_code == 'no_variable':
			message = 'No ' + details + ' variable within the ' + element_type + ' ID# ' + index_id
		elif err_code == 'invalid_amount':
			message = 'Invalid amount within ' + element_type + ' ID# ' + index_id + ', ' + details
		elif err_code == 'invalid_address':
			message = 'Invalid payment address within ' + element_type + ' ID# ' + index_id + ', ' + details
		elif err_code == 'invalid_vout':
			message = 'Invalid vout within ' + element_type + ' ID# ' + index_id + ', ' + details
		elif err_code == 'invalid_keyindex':
			message = 'Invalid keyindex within ' + element_type + ' ID# ' + index_id + ', ' + details
		elif err_code == 'invalid_sigscript':
			message = 'Invalid sigscript within ' + element_type + ' ID# ' + index_id + ', ' + details
		else:
			message = 'Unknown error'

		# Add to errors
		vars = {'type': err_code, 'index_id': index_id, 'message': message}
		self.json_errors.append(vars)

