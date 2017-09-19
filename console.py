
import sys, json, os.path, ctypes, ctypes.util
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from binascii import hexlify, unhexlify
from ui import *
from import_tx import *
from import_tx_results import *
from sign_single_tx import *
from help import *
from generate_master_key import *
from generate_hardened_child_key import *
from verify_public_key import *
from ecdsa_keys import *

class console(QMainWindow):
    
	def __init__(self):
		super(console, self).__init__()
		self.qss = {
			'header_label': "font-size: 14pt; font-weight: bold; margin-bottom: 5px;", 
			'description_label': "margin-bottom: 10px;"
		}
		#self.setStyleSheet("QLabel { font-family: Droid Dans; font-size: 10pt; color: #333; } QApplication { background: #ddd; }")
		self.initUI()

	def initUI(self):

		# Stacked widgets
		self.stack = QStackedWidget()
		self.stack.addWidget(import_tx(self))
		self.stack.addWidget(sign_single_tx(self))
		self.stack.addWidget(self.showui_bip32_keys())
		self.stack.addWidget(help(self))
		self.stack.addWidget(generate_master_key(self))
		self.stack.addWidget(generate_hardened_child_key(self))
		self.stack.addWidget(verify_public_key(self))
		self.setCentralWidget(self.stack)

		# Define menubar
		self.ui_define_menubar()

		# Define toolbar
		self.addToolBar(TopToolBar(self.stack))

		# Status bar
		self.statusBar().showMessage('Ready')

		# Display console
		self.setWindowTitle('Offline Tx Signer')
		self.setWindowIcon(QIcon("icons/bitcoin.png"))
		self.setMinimumWidth(700)

		# Center window
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())		

		# Show window
		self.show()

	def ui_define_menubar(self):

		# Initialize
		menubar = self.menuBar()

		# Define exit action
		exitAction = QAction('&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit application')
		exitAction.triggered.connect(self.close)

		# Define menu bar
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)

	def showui_bip32_keys(self):

		# Set widget
		widget = PanelWidget(self, 'BIP32 Keys', 'Here you may conduct various actions such as generate new BIP32 master keys, generate hardened child keys, and verify your public key.')
		widget.layout.addWidget(BIP32KeysToolBar(self.stack), 2, 0, 1, 2, Qt.AlignTop)

		# Return
		return widget


