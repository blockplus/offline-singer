
from PyQt4.QtGui import *
from PyQt4.QtCore import *

class LinkedLabel(QLabel):

	def __init__(self, text):
		super(LinkedLabel, self).__init__()
		self.setText(self.tr(text))
		self.setStyleSheet("font-size: 12px; color: blue;")
		self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)

	def enterEvent(self, event):
		QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))

	def leaveEvent(self, event):
		QApplication.restoreOverrideCursor()


class TopToolBar(QToolBar):

	def __init__(self, stack):
		super(TopToolBar, self).__init__()
		self.stack = stack
		self.setStyleSheet("background: #333; color: #fff;")
		self.setMovable(False)

		# Get toolbar buttons
		btnImport = TopBarButton("icons/import_tx.png", "Import")
		btnSign = TopBarButton("icons/sign_tx.png", "Sign")
		btnBIP32Keys = TopBarButton("icons/bip32_key.png", "BIP32 Keys")
		btnSettings = TopBarButton("icons/help.png", "Help")

		# Connect buttons
		btnImport.released.connect(self.ui_change_import_tx)
		btnSign.released.connect(self.ui_change_sign_tx)
		btnBIP32Keys.released.connect(self.ui_change_bip32_keys)
		btnSettings.released.connect(self.ui_change_settings)

		# Set left expanding widget
		leftBar = QWidget()
		leftBar.setStyleSheet("background: #333;")
		leftBar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

		# Add buttons to toolbar
		self.addWidget(btnImport)
		self.addWidget(btnSign)
		self.addWidget(btnBIP32Keys)
		self.addWidget(btnSettings)
		self.addWidget(leftBar)

	def ui_change_import_tx(self):
		self.stack.setCurrentIndex(0)

	def ui_change_sign_tx(self):
		self.stack.setCurrentIndex(1)

	def ui_change_bip32_keys(self):
		self.stack.setCurrentIndex(2)

	def ui_change_settings(self):
		self.stack.setCurrentIndex(3)

class TopBarButton(QToolButton):

	def __init__(self, icon, text):
		super(TopBarButton, self).__init__()
		self.setText(text)
		self.setIcon(QIcon(icon))
		self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
		self.setStyleSheet("width: 90px; background: #333; color: #fff;")

	def enterEvent(self, event):
		self.setStyleSheet("width: 90px; background: #bbb; color: #fff;")
		QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))

	def leaveEvent(self, event):
		self.setStyleSheet("width: 90px; background: #333; color: #fff;")
		QApplication.restoreOverrideCursor()

class BIP32KeysToolBar(QGroupBox):

	def __init__(self, stack):
		super(BIP32KeysToolBar, self).__init__()
		self.stack = stack

		# Button box
		layout = QVBoxLayout()
		self.setStyleSheet("margin-left: 10px;")
		self.setLayout(layout)

		# Create button
		btnGenerateMasterKey = BIP32ToolButton("icons/generate_master_key.png", self.tr("Generate Master Keys"))
		btnGenerateChildKey = BIP32ToolButton("icons/generate_child_key.png", self.tr("Generate Hardened Child Keys"))
		btnVerifyPubilcKey = BIP32ToolButton("icons/verify_public_key.png", self.tr("Verify Public Key"))

		# Connect actions for buttons
		btnGenerateMasterKey.released.connect(self.ui_change_generate_master_key)
		btnGenerateChildKey.released.connect(self.ui_change_generate_hardened_child_key)
		btnVerifyPubilcKey.released.connect(self.ui_change_verify_public_key)

		# Add buttons to box
		layout.addWidget(btnGenerateMasterKey, 0, Qt.AlignLeft)
		layout.addWidget(btnGenerateChildKey, 0, Qt.AlignLeft)
		layout.addWidget(btnVerifyPubilcKey, 0, Qt.AlignLeft)

	def ui_change_generate_master_key(self):
		self.stack.setCurrentIndex(4)

	def ui_change_generate_hardened_child_key(self):
		self.stack.setCurrentIndex(5)

	def ui_change_verify_public_key(self):
		self.stack.setCurrentIndex(6)

class BIP32ToolButton(QToolButton):

	def __init__(self, icon, text):
		super(BIP32ToolButton, self).__init__()
		self.setText(text)
		self.setIcon(QIcon(icon))
		self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.setStyleSheet("width: 500px; height: 30px; text-align: left; background: #333; color: #ffffff;")

	def enterEvent(self, event):
		self.setStyleSheet("width: 500px; height: 30px; text-align: left; background: #bbb; color: #ffffff;")
		QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))

	def leaveEvent(self, event):
		self.setStyleSheet("width: 500px; height: 30px; text-align: left; background: #333; color: #ffffff;")
		QApplication.restoreOverrideCursor()

class BIP32TextBox(QPlainTextEdit):

	def __init__(self, is_readonly = False):
		super(BIP32TextBox, self).__init__()
		self.setMaximumHeight(60)
		self.setReadOnly(is_readonly)
		if is_readonly == True:
			self.setStyleSheet("background: #ccc")

class HeaderLabel(QLabel):

	def __init__(self, text):
		super(HeaderLabel, self).__init__()
		self.setText(self.tr(text))
		self.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 5px;")

class DescriptionLabel(QLabel):

	def __init__(self, text):
		super(DescriptionLabel, self).__init__()
		self.setText(self.tr(text))
		self.setStyleSheet("margin-bottom: 10px;")
		self.setWordWrap(True)


class DownloadButton(QToolButton):

	def __init__(self):
		super(DownloadButton, self).__init__()
		self.setText("Download JSON File")
		self.setIcon(QIcon("icons/download.png"))
		self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
		self.setStyleSheet("width: 250px; height: 25px; text-align: left; background: #333; color: #ffffff;")

	def enterEvent(self, event):
		self.setStyleSheet("width: 250px; height: 25px; text-align: left; background: #bbb; color: #ffffff;")
		QApplication.setOverrideCursor(QCursor(Qt.PointingHandCursor))

	def leaveEvent(self, event):
		self.setStyleSheet("width: 250px; height: 25px; text-align: left; background: #333; color: #ffffff;")
		QApplication.restoreOverrideCursor()


class DataTable(QTableWidget):

	def __init__(self, columns = []):
		super(DataTable, self).__init__()
		
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setColumnCount(len(columns))
		self.setHorizontalHeaderLabels(columns)
		self.setStyleSheet("::section { padding: 4px; margin: 0px; }")
		self.rownum = 0


	def add_row(self, values = []):

		colnum = 0
		self.setRowCount(self.rownum + 1)
		for value in values:
			self.setItem(self.rownum, colnum, QTableWidgetItem(str(value)))
			colnum += 1

		self.rownum += 1


class PanelWidget(QWidget):

	def __init__(self, parent, header, description):
		super(PanelWidget, self).__init__()

		# Initialize
		self.layout = QGridLayout()
		self.layout.setAlignment(Qt.AlignTop)
		self.setLayout(self.layout)

		# Header
		lblHeader = QLabel(self.tr(header))
		lblHeader.setStyleSheet(parent.qss['header_label'])

		# Description
		lblDescription = QLabel(self.tr(description))
		lblDescription.setStyleSheet(parent.qss['description_label'])
		lblDescription.setWordWrap(True)

		# Add widgets to layout
		self.layout.addWidget(lblHeader, 0, 0, 1, 2, Qt.AlignTop)
		self.layout.addWidget(lblDescription, 1, 0, 1, 2, Qt.AlignTop)


