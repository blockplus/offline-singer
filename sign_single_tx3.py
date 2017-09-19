
import sys, json, os.path, re
from binascii import hexlify, unhexlify
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from rawtx import *
from sign_single_tx4 import *

class sign_single_tx3(QWidget):

	def __init__(self, parent, tx):
		super(sign_single_tx3, self).__init__()
		self.parent = parent
		self.tx = tx

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Sign Single Transaction'), 0, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(DescriptionLabel('To continue, enter the key index below for each input, and the necessary private key(s).  The key indexes should be provided by your online system, and if not, please contact your customer support.  Please note, if any inputs are from a multisig address, you will be required to enter multiple key indexes.  The order does not matter.'), 1, 0, 1, 2, Qt.AlignTop)

		# Go through inputs
		rownum = 2
		total_sigs = 1
		self.txtKeyIndex = {}
		for item in tx.inputs:
			input_id = hexlify(item['txid']) + ":" + str(item['vout'])
			if item['reqsigs'] > total_sigs:
				total_sigs = item['reqsigs']

			# Group box
			box = QGroupBox()
			boxLayout = QHBoxLayout()
			box.setLayout(boxLayout)
			box.setStyleSheet("QGroupBox { padding: 0px; margin-left: -12px; margin-top: -5px; }")

			# Add textboxes for key indexes
			for x in range (0, item['total_sigs']):
				txtkey = input_id + ":" + str(x)
				self.txtKeyIndex[txtkey] = QLineEdit()
				self.txtKeyIndex[txtkey].setMinimumWidth(60)
				self.txtKeyIndex[txtkey].setMaximumWidth(60)
				boxLayout.addWidget(self.txtKeyIndex[txtkey])

			# Add widgets
			layout.addWidget(QLabel('<b>Input #1</b>'), rownum, 0, 1, 2, Qt.AlignLeft)
			layout.addWidget(QLabel('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>TxID:</b>&nbsp;&nbsp;&nbsp;&nbsp;'), (rownum + 1), 0, 1, 1, Qt.AlignLeft)
			layout.addWidget(QLabel(hexlify(item['txid']) + ' (vout: ' + str(item['vout']) + ')'), (rownum + 1), 1, 1, 1, Qt.AlignLeft)
			layout.addWidget(QLabel('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Key Index:<b>'), (rownum + 2), 0, 1, 2, Qt.AlignLeft)
			layout.addWidget(box, (rownum + 2), 1, 1, 1, Qt.AlignLeft)
			rownum += 3

		# BIP32 Private Keys header
		lblBIP32PrivateKeys = QLabel('<b>BIP32 Private Keys</b>')
		lblBIP32PrivateKeys.setStyleSheet("margin-top: 20px;")
		layout.addWidget(lblBIP32PrivateKeys, (rownum + 1), 0, 1, 2, Qt.AlignLeft)
		rownum += 2

		# Add private key textboxes
		self.txtPrivKeys = [ ]
		for x in range (0, total_sigs):
			textbox = BIP32TextBox()
			layout.addWidget(QLabel('Private Key #' + str(x + 1) + ":"), rownum, 0, 1, 1, Qt.AlignTop)
			layout.addWidget(textbox, rownum, 1, 1, 1, Qt.AlignTop)
			self.txtPrivKeys.append(textbox)
			rownum += 1

		# Add push button
		self.buttonContinue = QPushButton(self.tr('Sign Transaction'), self)
		self.buttonContinue.setMaximumWidth(250)
		self.buttonContinue.clicked.connect(self.ok)
		layout.addWidget(self.buttonContinue, rownum, 1, 1, 1, Qt.AlignRight)


	def ok(self):

		# Initialize
		b32 = bip32()

		# Validate private keys
		privkeys = []
		for txt in self.txtPrivKeys:
			if str(txt.toPlainText()) == '':
				continue
			if b32.validate_ext_private_key(str(txt.toPlainText())) == False:
				QMessageBox.critical(self, "Error", "You did not specify a valid BIP32 private key.  Please double check, and try again.")
				return
			privkeys.append(str(txt.toPlainText()))

		# Go through inputs
		for item in self.tx.inputs:

			# Get key indexes
			keyindexes = []
			for x in range (0, item['total_sigs']):
				txtkey = hexlify(item['txid']) + ":" + str(item['vout']) + ':' + str(x)
				keyindexes.append(str(self.txtKeyIndex[txtkey].text()))

			# Validate input
			reqsigs, valid_privkeys = b32.validate_sigscript(item['sigscript'], privkeys, keyindexes)
			if valid_privkeys == False:
				QMessageBox.critical(self, "Error", "Unable to sign transaction with the provided information.  Please double check all information (private key, key index, scriptsig), and try again.")
				return
			else:
				item['privkeys'] = valid_privkeys
				item['reqsigs'] = reqsigs
				item['sigscript'] = unhexlify(item['sigscript'])

		# Sign tx
		signed_tx = self.tx.sign_transaction()

		# Show next screen
		w = sign_single_tx4(self.parent, self.tx, signed_tx)
		self.parent.stack.addWidget(w)
		self.parent.stack.setCurrentWidget(w)






