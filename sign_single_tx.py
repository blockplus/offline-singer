
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *
from rawtx import *
from sign_single_tx2 import *

class sign_single_tx(QWidget):

	def __init__(self, parent):
		super(sign_single_tx, self).__init__()
		self.parent = parent

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Text box
		self.txtRawHexCode = QPlainTextEdit()
		self.txtRawHexCode.setMaximumHeight(80)

		# Push button
		buttonSignSingleTx = QPushButton(self.tr('Sign Single Transaction'), self)
		buttonSignSingleTx.setMaximumWidth(250)
		buttonSignSingleTx.clicked.connect(self.ok)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Sign Single Transaction'), 0, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(DescriptionLabel('You may sign an individual transaction by entering the raw hex code of the transaction below.  This is the same hex code as the createrawtransaction() function from bitcoind will provide.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(QLabel(self.tr('Hex Code:  ')), 2, 0, Qt.AlignTop)
		layout.addWidget(self.txtRawHexCode, 2, 1, Qt.AlignTop)
		layout.addWidget(buttonSignSingleTx, 3, 1, 1, 1, Qt.AlignRight)


	def ok(self):

		# Decode transaction
		tx = rawtx()
		if tx.decode_transaction(self.txtRawHexCode.toPlainText()) == False:
			QMessageBox.critical(self, "Error", "Invalid transaction hex code submitted.  Please check your hex code, and try again.")
			return

		# Show next screen
		w = sign_single_tx2(self.parent, tx)
		self.parent.stack.addWidget(w)
		self.parent.stack.setCurrentWidget(w)



