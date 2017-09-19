#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
from console import *

def main():    
	app = QtGui.QApplication(sys.argv)
	ex = console()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()


