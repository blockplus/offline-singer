
import sys, json, os.path, re
from binascii import hexlify, unhexlify
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from rawtx import *

class sign_single_tx4(QWidget):

	def __init__(self, parent, tx, signed_tx):
		super(sign_single_tx4, self).__init__()
		self.parent = parent
		self.tx = tx

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Text box
		txtRawHexCode = QPlainTextEdit()
		txtRawHexCode.setMaximumHeight(250)
		txtRawHexCode.setPlainText(signed_tx)
		txtRawHexCode.setReadOnly(True)
		txtRawHexCode.setStyleSheet("background: #ccc")

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Transaction Signed'), 0, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(DescriptionLabel('The transaction has been successfully signed.  Below shows the hex code of the signed transaction, which must be broadcast to the blockchain to complete the send.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(QLabel('Hex Code:  '), 2, 0, 1, 1, Qt.AlignTop)
		layout.addWidget(txtRawHexCode, 2, 1, 1, 1, Qt.AlignTop)


