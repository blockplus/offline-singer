
import sys, json, os.path, re
from binascii import hexlify, unhexlify
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from rawtx import *
from sign_single_tx3 import *

class sign_single_tx2(QWidget):

	def __init__(self, parent, tx):
		super(sign_single_tx2, self).__init__()
		self.parent = parent
		self.tx = tx

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Sign Single Transaction'), 0, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(DescriptionLabel('To continue, enter the scriptsigs for each input shown below.  This information should be provided by your online system, and if not, please contact your customer support.'), 1, 0, 1, 2, Qt.AlignTop)

		# Go through inputs
		rownum = 2 
		input_num = 1
		self.txtSigScript = []
		for item in tx.inputs:

			# Sig Script text box
			textbox = QLineEdit()
			textbox.setMinimumWidth(400)
			self.txtSigScript.append(textbox)

			# Add widgets
			layout.addWidget(QLabel('<b>Input #' + str(input_num) + '</b>'), rownum, 0, 1, 2, Qt.AlignLeft)
			layout.addWidget(QLabel('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>TxID:</b>&nbsp;&nbsp;&nbsp;&nbsp;'), (rownum + 1), 0, 1, 1, Qt.AlignLeft)
			layout.addWidget(QLabel(hexlify(item['txid']) + ' (vout: ' + str(item['vout']) + ')'), (rownum + 1), 1, 1, 1, Qt.AlignLeft)
			layout.addWidget(QLabel('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>ScriptSig:<b>'), (rownum + 2), 0, 1, 2, Qt.AlignLeft)
			layout.addWidget(textbox, (rownum + 2), 1, 1, 1, Qt.AlignLeft)
			rownum += 3
			input_num += 1

		# Add push button
		self.buttonContinue = QPushButton(self.tr('Continue >>>'), self)
		self.buttonContinue.setMaximumWidth(250)
		self.buttonContinue.clicked.connect(self.ok)
		layout.addWidget(self.buttonContinue, (rownum + 1), 1, 1, 1, Qt.AlignRight)


	def ok(self):

		# Get sigscripts
		x = 0
		for textbox in self.txtSigScript:
			sig_script = str(textbox.text())
			s = re.match(r'76a914(.+?)88ac', sig_script, re.M|re.I)
			s2 = re.match(r'(..)(.*)(..)ae', sig_script, re.M|re.I)
			reqsigs = 0
			total_sigs = 0

			# Standard
			if s:
				reqsigs = 1
				total_sigs = 1

			# Multisig
			elif s2:
				reqsigs = (int(s2.group(1)) - 50)
				total_sigs = (int(s2.group(3)) - 50)

			else:
				QMessageBox.critical(self, "Error", "Invalid sig script submitted for input # " + x + ".  Please check the sig script, and try again.")
				return False

			self.tx.inputs[x]['sigscript'] = sig_script
			self.tx.inputs[x]['reqsigs'] = reqsigs
			self.tx.inputs[x]['total_sigs'] = total_sigs
			x += 1

		# Show next screen
		w = sign_single_tx3(self.parent, self.tx)
		self.parent.stack.addWidget(w)
		self.parent.stack.setCurrentWidget(w)

