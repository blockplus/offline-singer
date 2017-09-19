
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ui import *

class help(QWidget):

	def __init__(self, parent):
		super(help, self).__init__()
		self.parent = parent

		# Initialize
		layout = QGridLayout()
		layout.setAlignment(Qt.AlignTop)
		self.setLayout(layout)

		# Get help contents
		fh = open("help.html", 'r')
		html = fh.read()
		fh.close()

		# Help contents box
		txtHelp = QTextBrowser()
		txtHelp.setReadOnly(True)
		txtHelp.setSource(QUrl("help.html"))
		txtHelp.setMinimumHeight(400)
		txtHelp.verticalScrollBar().setValue(txtHelp.verticalScrollBar().maximum())

		# Add widgets to layout
		layout.addWidget(txtHelp, 0, 0, Qt.AlignTop)

		
