
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from bip32 import * 

class generate_hardened_child_key(QWidget):

	def __init__(self, parent):
		super(generate_hardened_child_key, self).__init__()
		self.parent = parent

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Textboxes
		self.txtMasterPrivKey = BIP32TextBox()
		self.txtChildPrivKey = BIP32TextBox(True)
		self.txtChildPubKey = BIP32TextBox(True)
		self.txtKeyIndex = QLineEdit()
		self.txtKeyIndex.setMaximumWidth(80)

		# Button box
		btnBox = QGroupBox()
		btnLayout = QHBoxLayout()
		btnBox.setLayout(btnLayout)
		btnBox.setStyleSheet("QGroupBox { margin: 0px; }")

		# Push Button - Back
		buttonBack = QPushButton(self.tr("< Back"), self)
		buttonBack.clicked.connect(self.back)

		# Push Button - Generate Key
		buttonGenChildKey = QPushButton('Generate Hardened Child Key', self)
		buttonGenChildKey.setMinimumWidth(250)
		buttonGenChildKey.clicked.connect(self.ok)

		# Add buttons to box
		btnLayout.addWidget(buttonBack)
		btnLayout.addWidget(buttonGenChildKey)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Generate Hardened Child Keys'), 0, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(DescriptionLabel('This allows you to generate "hardened" child keys, which is meant if you are using the hierarchial nature of BIP32 wallets, and will be handing out private keys to other people (eg.  employees, family, etc.).  Please see the help file for more details.  To continue, enter your existing BIP32 private key, and the desired key index below.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('BIP32 Private Key:  ')), 2, 0, Qt.AlignTop)
		layout.addWidget(self.txtMasterPrivKey, 2, 1, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Key Index (no \' mark):')), 3, 0, Qt.AlignTop)
		layout.addWidget(self.txtKeyIndex, 3, 1, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Child Private Key:  ')), 4, 0, Qt.AlignTop)
		layout.addWidget(self.txtChildPrivKey, 4, 1, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Child Public Key:  ')), 5, 0, Qt.AlignTop)
		layout.addWidget(self.txtChildPubKey, 5, 1, Qt.AlignTop)
		layout.addWidget(btnBox, 6, 1, Qt.AlignRight)

	def ok(self):

		# Initialize
		b32 = bip32(False)

		# Validate private key
		if b32.validate_ext_private_key(self.txtMasterPrivKey.toPlainText()) == False:
			QMessageBox.critical(self, "Error", "You did not specify a valid BIP32 private key.  Please double check, and try again.")
		
		# Generate master key
		privkey = b32.derive_child(self.txtMasterPrivKey.toPlainText(), self.txtKeyIndex.text(), True)
		pubkey = b32.ext_private_to_public(privkey)

		# Set textboxes
		self.txtChildPrivKey.setPlainText(privkey)
		self.txtChildPubKey.setPlainText(pubkey)

	def back(self):
		self.parent.stack.setCurrentIndex(2)

