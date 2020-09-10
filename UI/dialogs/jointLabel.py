# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *


class JointLabel(QDialog):
    def __init__(self, title="label joints", parent=None):
        super(JointLabel, self).__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(nullVBoxLayout())

        nameLabel = QLabel("Specify label sides (wildCards '*' can be used!):", self)
        L_txtLabel = QLabel("LeftSide", self)
        self.L_txt = QLineEdit("L_*", self)
        R_txtLabel = QLabel("RightSide", self)
        self.R_txt = QLineEdit("R_*", self)

        leftLayout = nullHBoxLayout()
        rightLayout = nullHBoxLayout()
        for w in [L_txtLabel, self.L_txt]:
            leftLayout.addWidget(w)
        for w in [R_txtLabel, self.R_txt]:
            rightLayout.addWidget(w)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        for wl in [nameLabel, leftLayout, rightLayout, buttonBox]:
            if isinstance(wl, QLayout):
                self.layout().addLayout(wl)
                continue
            self.layout().addWidget(wl)

    def verify(self):
        if not '' in [self.L_txt.text(), self.R_txt.text()] and self.L_txt.text() != self.R_txt.text():
            self.accept()
            return

        answer = QMessageBox.warning(self, "Incomplete Form",
                                     "The form does not contain all the necessary information.\n"
                                     "Continue with default settings?",
                                     QMessageBox.Yes, QMessageBox.No)

        if answer == QMessageBox.Yes:
            self.reject()
