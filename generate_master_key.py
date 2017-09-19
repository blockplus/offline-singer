
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from bip32 import *

class generate_master_key(QWidget):

	def __init__(self, parent):
		super(generate_master_key, self).__init__()
		self.parent = parent

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Textboxes
		self.txtMasterPrivKey = BIP32TextBox(True)
		self.txtMasterPubKey = BIP32TextBox(True)

		# Button box
		btnBox = QGroupBox()
		btnLayout = QHBoxLayout()
		btnBox.setLayout(btnLayout)
		btnBox.setStyleSheet("QGroupBox { margin: 0px; }")

		# Push Button - Back
		buttonBack = QPushButton(self.tr("< Back"), self)
		buttonBack.clicked.connect(self.back)

		# Push Button - Generate Key
		buttonGenMasterKey = QPushButton(self.tr('Generate Master Key'), self)
		buttonGenMasterKey.setMinimumWidth(200)
		buttonGenMasterKey.clicked.connect(self.ok)

		# Add buttons to box
		btnLayout.addWidget(buttonBack)
		btnLayout.addWidget(buttonGenMasterKey)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Generate Master BIP32 Key'), 0, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(DescriptionLabel('You may generate new master BIP32 key pairs by pressing the below button.  All keys are genererated with a random 8192 bit key.  The private key should ALWAYS remain offline, whereas you will most likely need the public key for your online software system.<br><br><b>NOTE:</b> You may click the generate key as many times as you like, and each time will generate a new, random 8192 bit key pair.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Private Key:  ')), 2, 0, Qt.AlignTop)
		layout.addWidget(self.txtMasterPrivKey, 2, 1, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Public Key:  ')), 3, 0, Qt.AlignTop)
		layout.addWidget(self.txtMasterPubKey, 3, 1, Qt.AlignTop)
		layout.addWidget(btnBox, 4, 1, Qt.AlignRight)

	def ok(self):

		# Initialize
		testnet = False
		b32 = bip32(testnet)
		
		# Generate master key
		privkey = b32.generate_master_key()
		pubkey = b32.ext_private_to_public(privkey)

		# Set textboxes
		self.txtMasterPrivKey.setPlainText(privkey)
		self.txtMasterPubKey.setPlainText(pubkey)

	def back(self):
		self.parent.stack.setCurrentIndex(2)
