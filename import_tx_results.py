
import sys, json, os.path, re
from binascii import hexlify, unhexlify
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *

class import_tx_results(QWidget):

	def __init__(self, json = None):
		super(import_tx_results, self).__init__()
		self.json = json

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Summary group box
		boxSummary = QGroupBox();
		boxSummary.setStyleSheet("width: 650px; margin: 0px;")
		layoutSummary = QGridLayout()
		boxSummary.setLayout(layoutSummary)

		# Set summary labels
		self.lblTotalInputs = QLabel('N/A')
		self.lblTotalOutputs = QLabel('N/A')
		self.lblTotalChange = QLabel('N/A')

		# Push button
		buttonDownloadJSONFile = DownloadButton()
		buttonDownloadJSONFile.released.connect(self.save_json_file)

		# View box
		boxView = QGroupBox()
		layoutView = QHBoxLayout()
		boxView.setLayout(layoutView)
		boxView.setStyleSheet("margin: 0px; padding: 0px; border: 0px;")

		# Add radio buttons & labels to view box
		radioViewOutputs = QRadioButton(self.tr('Outputs'))
		radioViewInputs = QRadioButton(self.tr('Spent Inputs'))
		radioViewChange = QRadioButton(self.tr('Change Txs'))
		radioViewOutputs.setChecked(True)
		layoutView.addWidget(radioViewOutputs)
		layoutView.addWidget(radioViewInputs)
		layoutView.addWidget(radioViewChange)

		# Connect radio boxes
		radioViewOutputs.clicked.connect(self.chk_view_outputs)
		radioViewInputs.clicked.connect(self.chk_view_inputs)
		radioViewChange.clicked.connect(self.chk_view_change)

		# Outputs table
		self.tblOutputs = DataTable(['Address', 'Amount', 'Input', 'Change', 'Txid'])
		self.tblOutputs.setColumnWidth(0, 300)

		# Inputs table
		self.tblInputs = DataTable(['Amount', 'Txid', 'Vout', 'Sigscript'])
		self.tblInputs.setColumnWidth(1, 300)
		self.tblInputs.setColumnWidth(2, 50)
		self.tblInputs.setColumnWidth(3, 300)

		# Change table
		self.tblChange = DataTable(['Amount', 'Address', 'Txid', 'Vout', 'Sigscript'])
		self.tblChange.setColumnWidth(1, 300)
		self.tblChange.setColumnWidth(2, 200)
		self.tblChange.setColumnWidth(3, 50)
		self.tblChange.setColumnWidth(4, 300)

		# Stacked widget
		self.stack = QStackedWidget()
		self.stack.addWidget(self.tblOutputs)
		self.stack.addWidget(self.tblInputs)
		self.stack.addWidget(self.tblChange)

		# Add widgets to summary box
		layoutSummary.addWidget(QLabel(self.tr('<b>Total Input:</b>')), 0, 0, Qt.AlignTop)
		layoutSummary.addWidget(QLabel(self.tr('<b>Total Output:</b>')), 1, 0, Qt.AlignTop)
		layoutSummary.addWidget(QLabel(self.tr('<b>Total Change:</b>')), 2, 0, Qt.AlignTop)
		layoutSummary.addWidget(self.lblTotalInputs, 0, 1, Qt.AlignTop)
		layoutSummary.addWidget(self.lblTotalOutputs, 1, 1, Qt.AlignTop)
		layoutSummary.addWidget(self.lblTotalChange, 2, 1, Qt.AlignTop)
		layoutSummary.addWidget(buttonDownloadJSONFile, 0, 2, 3, 1, Qt.AlignTop)

		# Add widgets to layout
		layout.addWidget(HeaderLabel('Signing Results'), 0, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(DescriptionLabel('Below shows all results of the signing operation.  When ready, click the button below to download the JSON file of signed transactions, which you must upload into the online system to complete the sends.'), 1, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(boxSummary, 2, 0, 1, 2, Qt.AlignTop)
		layout.addWidget(boxView, 3, 0, 1, 2, Qt.AlignLeft)
		layout.addWidget(self.stack, 4, 0, 1, 2, Qt.AlignTop)


	def populate_results(self, json):
		self.json = json

		# Initialize variables		
		input_amount = 0
		output_amount = 0
		change_amount = 0
		input_ids = []

		# Go through spent inputs
		for item in json['spent_inputs']:
			input_amount += float(item['amount'])
			self.tblInputs.add_row([self.format_amount(float(item['amount'])), item['txid'], item['vout'], item['sigscript']])
			input_ids.append(item['input_id'])

		# Go through transactions
		for item in json['tx']:
			output_amount += float(item['amount'])
			change_amount += float(item['change_amount'])
			self.tblOutputs.add_row([item['to_address'], self.format_amount(item['amount']), self.format_amount(item['input_amount']), self.format_amount(item['change_amount']), item['txid']])


		# Set labels
		self.lblTotalInputs.setText(self.format_amount(input_amount) + ' (' + str(len(json['spent_inputs'])) + ' inputs)')
		self.lblTotalOutputs.setText(self.format_amount(output_amount) + ' (' + str(len(json['tx'])) + ' transactions)')
		self.lblTotalChange.setText(self.format_amount(change_amount))


	def format_amount(self, amount):

		amount = ("%.8f" % amount)
		s = re.match(r'^(.+)0000$', amount, re.M|re.I)
		if s:
			amount = s.group(1)

		return amount

	def save_json_file(self):

		# Save JSON file
		save_filename = QFileDialog.getSaveFileName(self, "Save Transaction File", "signedtx.json", "JSON files (*.*)")
		if save_filename != '':
			with open(save_filename, 'w') as outfile:
				json.dump(self.json, outfile)
				QMessageBox.information(self, 'JSON File Saved', "The new JSON file of signed transactions has been successfully saved.  Please upload it into the online system to complete the sends.")


	def chk_view_outputs(self):
		self.stack.setCurrentIndex(0)

	def chk_view_inputs(self):
		self.stack.setCurrentIndex(1)

	def chk_view_change(self):
		self.stack.setCurrentIndex(2)


