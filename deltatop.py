import sys
import delta_sharing
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QComboBox

class DeltaSharingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Delta Sharing Data Downloader')
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel('Delta Sharing Data Downloader', self)
        layout.addWidget(title_label)

        instruction_label = QLabel('Choose your config.share file to download the table as a CSV file.', self)
        layout.addWidget(instruction_label)

        self.file_label = QLabel('Choose your config.share file', self)
        layout.addWidget(self.file_label)

        self.upload_button = QPushButton('Select config.share', self)
        self.upload_button.clicked.connect(self.upload_config)
        layout.addWidget(self.upload_button)

        self.share_combo = QComboBox(self)
        self.share_combo.setEnabled(False)
        layout.addWidget(self.share_combo)

        self.schema_combo = QComboBox(self)
        self.schema_combo.setEnabled(False)
        layout.addWidget(self.schema_combo)

        self.table_combo = QComboBox(self)
        self.table_combo.setEnabled(False)
        layout.addWidget(self.table_combo)

        self.download_button = QPushButton('Download Data', self)
        self.download_button.clicked.connect(self.download_data)
        self.download_button.setEnabled(False)
        layout.addWidget(self.download_button)

        self.status_label = QLabel('', self)
        layout.addWidget(self.status_label)

    def upload_config(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select config.share File", "", "Share Files (*.share);;All Files (*)", options=options)
        if file_path:
            self.config_path = file_path
            self.file_label.setText(f"Selected: {file_path}")
            self.load_share_options()

    def load_share_options(self):
        try:
            self.client = delta_sharing.SharingClient(self.config_path)
            self.all_tables = self.client.list_all_tables()
            shares = list(set(table.share for table in self.all_tables))
            self.share_combo.clear()
            self.share_combo.addItems(shares)
            self.share_combo.setEnabled(True)
            self.share_combo.setCurrentIndex(0)
            self.share_combo.currentTextChanged.connect(self.load_schema_options)
            self.load_schema_options(shares[0])
            self.status_label.setText("Share options loaded.")
        except Exception as e:
            self.status_label.setText(f"Error loading shares: {str(e)}")

    def load_schema_options(self, share):
        schemas = list(set(table.schema for table in self.all_tables if table.share == share))
        self.schema_combo.clear()
        self.schema_combo.addItems(schemas)
        self.schema_combo.setEnabled(True)
        self.schema_combo.setCurrentIndex(0)
        self.schema_combo.currentTextChanged.connect(lambda: self.load_table_options(share))
        self.load_table_options(share)
        self.status_label.setText("Schema options loaded.")

    def load_table_options(self, share):
        schema = self.schema_combo.currentText()
        tables = [table.name for table in self.all_tables if table.share == share and table.schema == schema]
        self.table_combo.clear()
        self.table_combo.addItems(tables)
        self.table_combo.setEnabled(True)
        self.table_combo.setCurrentIndex(0)
        self.download_button.setEnabled(True)
        self.status_label.setText("Table options loaded. Ready to download data.")

    def download_data(self):
        try:
            share = self.share_combo.currentText()
            schema = self.schema_combo.currentText()
            table = self.table_combo.currentText()
            table_url = f"{self.config_path}#{share}.{schema}.{table}"
            
            data = delta_sharing.load_as_pandas(table_url)

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Data As", "", "CSV Files (*.csv);;All Files (*)")
            if save_path:
                data.to_csv(save_path, index=False)
                self.status_label.setText(f"Data downloaded and saved to {save_path}")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DeltaSharingApp()
    ex.show()
    sys.exit(app.exec_())
