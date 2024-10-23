import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from pathlib import Path
import tempfile
from reservation_formatter import ReservationFormatter

class CalendarApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.formatter = ReservationFormatter()
        self.initUI()
        
    def initUI(self):
        """UIの初期化"""
        self.setWindowTitle('予約カレンダー登録')
        self.setMinimumSize(400, 300)
        
        # メインウィジェット
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # ドロップエリアの作成
        self.drop_area = QWidget()
        self.drop_area.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 2px dashed #999;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        drop_layout = QVBoxLayout(self.drop_area)
        
        # 説明ラベル
        icon_label = QLabel("📅")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        drop_layout.addWidget(icon_label)
        
        instruction_label = QLabel('予約画面のスクリーンショットを\nここにドロップしてください')
        instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                margin: 10px;
            }
        """)
        drop_layout.addWidget(instruction_label)
        
        layout.addWidget(self.drop_area)
        
        # ステータス表示
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                padding: 10px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # ドラッグ&ドロップの設定
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """ドラッグ開始時の処理"""
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                event.acceptProposedAction()
                self.drop_area.setStyleSheet("""
                    QWidget {
                        background-color: #e3f2fd;
                        border: 2px dashed #2196f3;
                        border-radius: 10px;
                        margin: 20px;
                    }
                """)
                self.status_label.setText("ここにドロップしてください")
                self.status_label.setStyleSheet("color: #2196f3;")

    def dragLeaveEvent(self, event):
        """ドラッグ終了時の処理"""
        self.drop_area.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 2px dashed #999;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        self.status_label.setText("")

    def dropEvent(self, event):
        """ドロップ時の処理"""
        try:
            self.status_label.setText("ファイルを処理中...")
            self.status_label.setStyleSheet("color: #1976d2;")
            QApplication.processEvents()

            file_path = event.mimeData().urls()[0].toLocalFile()
            
            with tempfile.NamedTemporaryFile(suffix='.ics', delete=False) as tmp:
                output_path = Path(tmp.name)
            
            success, calendar_name = self.formatter.process(
                Path(file_path),
                output_path
            )
            
            if success:
                self.status_label.setText(f"予約を {calendar_name} に追加しました")
                self.status_label.setStyleSheet("color: #2e7d32;")
            else:
                self.status_label.setText("処理に失敗しました")
                self.status_label.setStyleSheet("color: #c62828;")
                
            event.acceptProposedAction()
            
        except Exception as e:
            self.status_label.setText(f"エラー: {str(e)}")
            self.status_label.setStyleSheet("color: #c62828;")

def main():
    app = QApplication(sys.argv)
    calendar_app = CalendarApp()
    calendar_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()