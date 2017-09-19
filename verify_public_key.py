
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from bip32 import *

class verify_public_key(QWidget):

	def __init__(self, parent):
		super(verify_public_key, self).__init__()
		self.parent = parent

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Textboxes
		self.txtMasterPrivKey = BIP32TextBox()
		self.txtMasterPubKey = BIP32TextBox(True)

		# Button box
		btnBox = QGroupBox()
		btnLayout = QHBoxLayout()
		btnBox.setLayout(btnLayout)
		btnBox.setStyleSheet("QGroupBox { margin: 0px; }")

		# Push Button - Back
		buttonBack = QPushButton(self.tr("< Back"), self)
		buttonBack.clicked.connect(self.back)

		# Push Button - Generate Public Key
		buttonVerifyKey = QPushButton(self.tr('Generate Public Key'), self)
		buttonVerifyKey.setMinimumWidth(200)
		buttonVerifyKey.clicked.connect(self.ok)

		# Add buttons to box
		btnLayout.addWidget(buttonBack)
		btnLayout.addWidget(buttonVerifyKey)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Verify Public Key'), 0, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(DescriptionLabel('You may verify your BIP32 public key by entering the private key below.  In return, the public key that corresponds to the private key will be shown.  This allows you to ensure the public key within the online system has not been replaced.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Private Key:  ')), 2, 0, Qt.AlignTop)
		layout.addWidget(self.txtMasterPrivKey, 2, 1, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Public Key:  ')), 3, 0, Qt.AlignTop)
		layout.addWidget(self.txtMasterPubKey, 3, 1, Qt.AlignTop)
		layout.addWidget(btnBox, 4, 1, Qt.AlignRight)

	def ok(self):

		# Validate public key
		b32 = bip32()
		if b32.validate_ext_private_key(self.txtMasterPrivKey.toPlainText()) == False:
			QMessageBox.critical(self, "Error", "You did not specify a valid BIP32 private key.  Please double check, and try again.")
			return

		# Get public key
		pubkey = b32.ext_private_to_public(self.txtMasterPrivKey.toPlainText())
		self.txtMasterPubKey.setPlainText(pubkey)

	def back(self):
		self.parent.stack.setCurrentIndex(2)

