from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QCursor, QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QProgressBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Out")
        self.setFixedSize(600, 900)
        self.setWindowIcon(QIcon("imagens/icon.png"))

        # background
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("imagens/main.png"))
        self.background.setGeometry(0, 0, 600, 900)
        self.background.setScaledContents(True)

        # botao play
        self.play_button = QPushButton(self)
        self.play_button.setIcon(QIcon("imagens/botao_play.png"))
        self.play_button.setIconSize(QSize(500, 500))
        self.play_button.setGeometry(5, 700, 600, 200)
        self.play_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.play_button.setStyleSheet("border: none;")
        self.play_button.clicked.connect(self.show_loading)

    def show_loading(self):
        self.loading = SplashScreen()
        self.loading.show()
        self.close()


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Carregando...")
        self.setFixedSize(600, 400)
        #self.setStyleSheet("background-color: white;")

        # Fundo com imagem
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("imagens/fundo_loading.png"))  # <-- usa a tua imagem aqui
        self.background.setGeometry(0, 0, 600, 400)
        self.background.setScaledContents(True)

        # Mensagem de carregamento
        self.label = QLabel("A iniciar o Park Out...", self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(0, 100, 600, 60)

        # Barra de progresso
        self.progress = QProgressBar(self)
        self.progress.setGeometry(100, 200, 400, 30)
        self.progress.setMaximum(100)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 10px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)

        # Timer de carregamento
        self.counter = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)  # 100 × 50ms = 5 segundos

    def update_progress(self):
        if self.counter >= 100:
            self.timer.stop()
            self.abrir_janela_principal()
        else:
            self.counter += 1
            self.progress.setValue(self.counter)

    def abrir_janela_principal(self):
        self.novajanela = Novajanela()
        self.novajanela.show()
        self.close()


class Novajanela(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Park Out")
        self.setFixedSize(600, 900)
        self.background = QLabel(self)
        self.background.setPixmap(QPixmap("imagens/principal.png"))
        self.background.setGeometry(0, 0, 600, 900)
        self.background.setScaledContents(True)





        