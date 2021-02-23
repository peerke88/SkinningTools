# -*- coding: utf-8 -*-
from SkinningTools.UI.qt_util import *
from SkinningTools.UI.utils import *


class JointName(QDialog):
    def __init__(self, title="name joint", parent=None):
        super(JointName, self).__init__(parent)
        self.setWindowTitle(title)
        self.setLayout(nullVBoxLayout())
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        nameLabel = QLabel("give name to the joint to be created:", self)
        txtLabel = QLabel("name:", self)
        self.txt = QLineEdit("", self)

        leftLayout = nullHBoxLayout()
        for w in [txtLabel, self.txt]:
            leftLayout.addWidget(w)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.verify)
        buttonBox.rejected.connect(self.reject)

        for wl in [nameLabel, leftLayout, buttonBox]:
            if isinstance(wl, QLayout):
                self.layout().addLayout(wl)
                continue
            self.layout().addWidget(wl)

    def verify(self):
        if not '' in [self.txt.text()]:
            self.accept()
            return

        answer = QuickDialog("Incomplete Form")
        answer.layout(insertWidget(0, QLabel("Continue with default settings?")))
        answer.layout(insertWidget(0, QLabel("The form does not contain all the necessary information.")))
        # answer = QMessageBox.warning(self, "Incomplete Form",
        #                              "The form does not contain all the necessary information.\n"
        #                              "Continue with default settings?",
        #                              QMessageBox.Yes, QMessageBox.No)

        if answer.result() == 0:
            self.reject()

