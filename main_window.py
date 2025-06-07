# Importação de módulos
import os
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint

# Diretórios com imagens dos carros e suas cores correspondentes
IMAGE_FOLDERS = [
    ("imagens/autocarros/autocarrosamarelos", "amarelo"),
    ("imagens/autocarros/autocarrosazuis", "azul"),
    ("imagens/autocarros/autocarrosverdes", "verde"),
    ("imagens/autocarros/autocarrosvermelhos", "vermelho"),
]

# Diretórios com imagens das pessoas e suas cores correspondentes
PEOPLE_FOLDERS = [
    ("imagens/pessoas/amarelo", "amarelo"),
    ("imagens/pessoas/azul", "azul"),
    ("imagens/pessoas/verde", "verde"),
    ("imagens/pessoas/vermelho", "vermelho"),
]

# Classe que representa um carro
class CarroWidget(QLabel):
    def __init__(self, imagem_path, cor, mover_callback, capacidade, parent=None):
        super().__init__(parent)
        self.capacidade = capacidade
        self.ocupacao_atual = 0
        self.imagem_path = imagem_path
        self.cor_carro = cor.lower().strip()
        self.mover_callback = mover_callback

        # Define a direção do carro com base no nome da imagem
        nome_ficheiro = os.path.basename(imagem_path).lower()
        if "up" in nome_ficheiro:
            self.direcao = "up"
        elif "down" in nome_ficheiro:
            self.direcao = "down"
        elif "left" in nome_ficheiro:
            self.direcao = "left"
        elif "right" in nome_ficheiro:
            self.direcao = "right"
        else:
            self.direcao = "up"

        self.setFixedSize(70, 70)
        self.setStyleSheet("background: transparent; border: none;")

        # Define imagem do carro
        pixmap = QPixmap(imagem_path)
        if not pixmap.isNull():
            self.setPixmap(pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.setText("Erro imagem")

        # Label que mostra ocupação atual do carro
        self.ocupacao_label = QLabel(f"{self.ocupacao_atual}/{self.capacidade}", self)
        self.ocupacao_label.setStyleSheet("color: black; font-size: 10px; background-color: rgba(255,255,255,150);")
        self.ocupacao_label.move(2, 50)
        self.ocupacao_label.resize(60, 15)
        self.ocupacao_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ocupacao_label.hide()

    def mousePressEvent(self, event):
        self.mover_callback(self)  # Chama a função para mover o carro

    def atualizar_ocupacao(self):
        self.ocupacao_label.setText(f"{self.ocupacao_atual}/{self.capacidade}")

# Classe que representa uma pessoa
class PessoaWidget(QLabel):
    def __init__(self, imagem_path, cor, parent=None):
        super().__init__(parent)
        self.imagem_path = imagem_path
        self.cor = cor.lower().strip()
        self.setFixedSize(100, 100)
        self.setStyleSheet("background: transparent; border: none;")

        pixmap = QPixmap(imagem_path)
        if not pixmap.isNull():
            self.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.setText("Erro imagem")

# Janela principal do jogo
class Novajanela(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Park Out")
        self.setWindowIcon(QIcon("imagens/icon.png"))
        self.setFixedSize(600, 800)

        # Define o fundo da janela
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        bg_path = "imagens/principal.png"
        if os.path.exists(bg_path):
            self.central_widget.setStyleSheet(f"QWidget {{ background-image: url({bg_path}); background-repeat: no-repeat; background-position: center; background-size: cover; }}")
        else:
            self.central_widget.setStyleSheet("QWidget { background-color: #cccccc; }")

        # Coordenadas possíveis para estacionamento dos carros
        self.vagas_disponiveis = [(50, 150), (140, 150), (230, 150), (320, 150), (400, 150), (490, 150)]
        self.ocupadas = {}

        # Parâmetros da grelha
        self.num_rows = 5
        self.num_cols = 5
        self.total_slots = self.num_rows * self.num_cols

        # Carrega imagens dos carros e pessoas
        self.images_by_folder = [self.load_images_from_folder(folder) for folder, _ in IMAGE_FOLDERS]
        colors = [cor for _, cor in IMAGE_FOLDERS]
        self.image_paths_com_cores = self.prepare_balanced_images_with_colors(self.images_by_folder, colors, self.total_slots)
        self.people_images_colored = self.load_people_with_colors()

        self.carros_widgets = []

        # Gera número de pessoas aleatório
        capacidades_possiveis = [4, 6, 8, 12]
        self.numero_aleatorio = random.randint(100, 120)
        print(f"Número alvo de pessoas: {self.numero_aleatorio}")

        capacidades_carros = self.criar_capacidades_exatas(self.numero_aleatorio)

        # Criação e posicionamento dos carros na grelha
        start_x, start_y = 150, 400
        spacing_x, spacing_y = 70, 70

        for index in range(self.total_slots):
            imagem_path, cor = self.image_paths_com_cores[index]
            capacidade = capacidades_carros[index]

            carro = CarroWidget(imagem_path, cor, self.mover_carro_para_vaga, capacidade, parent=self.central_widget)
            row, col = index // self.num_cols, index % self.num_cols
            carro.move(start_x + col * spacing_x, start_y + row * spacing_y)
            carro.show()
            self.carros_widgets.append(carro)

        # Prepara fila de reserva de pessoas
        self.fila_reserva = []
        while len(self.fila_reserva) < self.numero_aleatorio:
            faltam = self.numero_aleatorio - len(self.fila_reserva)
            if faltam >= len(self.people_images_colored):
                self.fila_reserva.extend(self.people_images_colored)
            else:
                self.fila_reserva.extend(random.sample(self.people_images_colored, faltam))

        self.fila_visivel = []
        self.max_pessoas_fila = 7

        # Mostra número de pessoas restantes
        self.numero_label = QLabel(f"{self.numero_aleatorio}", self.central_widget)
        self.numero_label.setStyleSheet("font-size: 24px; font-weight: bold; color: black;")
        self.numero_label.adjustSize()
        self.numero_label.move(50, 50)

        # Botão para reiniciar o jogo
        self.restart_button = QPushButton("Restart", self.central_widget)
        self.restart_button.setStyleSheet("font-size: 16px; padding: 6px;")
        self.restart_button.move(500, 350)
        self.restart_button.clicked.connect(self.reiniciar_jogo)
        self.restart_button.show()

        # Cria a fila de pessoas visível
        self.create_fila_linear()

        # Timer que chama a função de entrada de pessoas periodicamente
        self.timer = QTimer()
        self.timer.timeout.connect(self.tentar_entrar_pessoa)
        self.timer.start(1000)

    # (Demais métodos também estão comentados no estilo acima, mas foram ocultados por brevidade.)

    def criar_capacidades_exatas(self, total_pessoas):
        capacidades_possiveis = [4, 6, 8, 12]  # Capacidades válidas para os carros
        n_carros = self.total_slots  # Número total de carros, por exemplo 25

        capacidades = [4] * n_carros  # Inicializa todos os carros com capacidade mínima 4
        soma = sum(capacidades)  # Soma inicial (exemplo: 25 carros * 4 = 100)

        diferenca = total_pessoas - soma  # Quantidade que falta para atingir total_pessoas

        # Distribui essa diferença aleatoriamente entre os carros, respeitando o máximo 12 por carro
        indices = list(range(n_carros))
        random.shuffle(indices)  # Embaralha índices para distribuição aleatória

        for i in indices:
            if diferenca <= 0:
                break  # Se já alcançou ou ultrapassou o total, para
            max_incr = 12 - capacidades[i]  # Quanto ainda pode aumentar a capacidade do carro i
            incr = min(diferenca, max_incr)  # Quanto será incrementado efetivamente
            capacidades[i] += incr
            diferenca -= incr

        # Ajusta as capacidades para os valores válidos mais próximos (4,6,8,12)
        def nearest_valid(val):
            return min(capacidades_possiveis, key=lambda x: abs(x - val))

        capacidades = [nearest_valid(c) for c in capacidades]

        # Ajuste fino para tentar chegar exatamente no total_pessoas
        diff = total_pessoas - sum(capacidades)
        max_tentativas = 1000
        tentativas = 0

        while diff != 0 and tentativas < max_tentativas:
            tentativas += 1
            for i in range(n_carros):
                if diff == 0:
                    break
                atual = capacidades[i]
                idx = capacidades_possiveis.index(atual)

                if diff > 0 and idx < len(capacidades_possiveis) - 1:
                    incremento = capacidades_possiveis[idx + 1] - atual
                    if incremento <= diff:
                        capacidades[i] = capacidades_possiveis[idx + 1]
                        diff -= incremento
                elif diff < 0 and idx > 0:
                    decremento = atual - capacidades_possiveis[idx - 1]
                    if decremento <= abs(diff):
                        capacidades[i] = capacidades_possiveis[idx - 1]
                        diff += decremento

        # Se não foi possível ajustar perfeitamente, avisa o usuário
        if diff != 0:
            print(f"[Aviso] Não foi possível atingir exatamente {total_pessoas}. Diferença final: {diff}")

        return capacidades

    def reiniciar_jogo(self):
        self.timer.stop()  # Para o temporizador da interface (animações ou eventos periódicos)

        # Remove todos os carros da tela e limpa a lista
        for carro in self.carros_widgets:
            carro.hide()
            carro.deleteLater()
        self.carros_widgets.clear()
        self.ocupadas.clear()

        # Remove todas as pessoas visíveis e limpa filas
        for pessoa in self.fila_visivel:
            pessoa.hide()
            pessoa.deleteLater()
        self.fila_visivel.clear()
        self.fila_reserva.clear()

        # Gera um novo número aleatório de pessoas para o jogo, entre 100 e 120
        self.numero_aleatorio = random.randint(100, 120)
        self.numero_label.setText(str(self.numero_aleatorio))
        self.numero_label.adjustSize()

        # Cria capacidades para os carros que somam esse número aleatório de pessoas
        capacidades_carros = self.criar_capacidades_exatas(self.numero_aleatorio)

        # Define posições iniciais e espaçamento para os carros na grade
        start_x = 150
        start_y = 400
        spacing_x = 70
        spacing_y = 70

        # Cria os carros novamente, posiciona e exibe
        for index in range(self.total_slots):
            imagem_path, cor = self.image_paths_com_cores[index]
            capacidade = capacidades_carros[index]

            carro = CarroWidget(imagem_path, cor, self.mover_carro_para_vaga, capacidade, parent=self.central_widget)
            row = index // self.num_cols
            col = index % self.num_cols
            carro.move(start_x + col * spacing_x, start_y + row * spacing_y)
            carro.show()

            self.carros_widgets.append(carro)

        # Recria a fila de pessoas para embarque, até o número de pessoas necessário
        while len(self.fila_reserva) < self.numero_aleatorio:
            faltam = self.numero_aleatorio - len(self.fila_reserva)
            if faltam >= len(self.people_images_colored):
                self.fila_reserva.extend(self.people_images_colored)
            else:
                self.fila_reserva.extend(random.sample(self.people_images_colored, faltam))

        self.create_fila_linear()  # Cria a fila visível para o usuário

        self.timer.start()  # Reinicia o temporizador

    def load_images_from_folder(self, folder_path):
        all_image_paths = []
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    filepath = os.path.join(folder_path, filename)
                    all_image_paths.append(filepath)
        return all_image_paths

    def prepare_balanced_images_with_colors(self, images_by_folder, colors, total_slots):
        balanced = []
        n_folders = len(images_by_folder)
        slots_per_folder = total_slots // n_folders
        extra = total_slots % n_folders

        for i, (images, cor) in enumerate(zip(images_by_folder, colors)):
            if images:
                count = slots_per_folder + (1 if i < extra else 0)
                chosen = []
                while len(chosen) < count:
                    chosen.extend(random.sample(images, min(count - len(chosen), len(images))))
                balanced.extend([(img, cor) for img in chosen])
        random.shuffle(balanced)
        return balanced

    def load_people_with_colors(self):
        pessoas = []
        for folder, cor in PEOPLE_FOLDERS:
            imagens = self.load_images_from_folder(folder)
            for img in imagens:
                pessoas.append((img, cor))
        if not pessoas:
            pessoas.append(("imagens/default_person.png", "amarelo"))
        return pessoas

    def create_fila_linear(self):
        for pessoa in self.fila_visivel:
            pessoa.hide()
            pessoa.deleteLater()
        self.fila_visivel.clear()

        self.fila_start_x = 150
        self.fila_start_y = 25
        self.fila_spacing_x = 60

        for i in range(min(self.max_pessoas_fila, len(self.fila_reserva))):
            imagem_path, cor = self.fila_reserva.pop(0)
            pessoa = PessoaWidget(imagem_path, cor, parent=self.central_widget)
            pessoa.move(self.fila_start_x + i * self.fila_spacing_x, self.fila_start_y)
            pessoa.show()
            self.fila_visivel.append(pessoa)

    def mover_carro_para_vaga(self, carro_widget):
        if not self.caminho_livre(carro_widget):
            print("Caminho bloqueado. Não pode mover.")
            return

        vaga_livre = next((vaga for vaga in self.vagas_disponiveis if vaga not in self.ocupadas), None)
        if vaga_livre is None:
            print("Sem vagas livres para o carro.")
            return

        vaga_antiga = next((coord for coord, carro in self.ocupadas.items() if carro == carro_widget), None)
        if vaga_antiga is not None:
            del self.ocupadas[vaga_antiga]

        animation = QPropertyAnimation(carro_widget, b"pos", self)
        animation.setDuration(500)
        animation.setStartValue(carro_widget.pos())
        animation.setEndValue(QPoint(*vaga_livre))
        animation.start()
        carro_widget.animation = animation
        carro_widget.ocupacao_label.show()
        self.ocupadas[vaga_livre] = carro_widget

    def tentar_entrar_pessoa(self):
        # Se a fila visível estiver vazia, nada a fazer
        if not self.fila_visivel:
            return

        primeira_pessoa = self.fila_visivel[0]
        cor_pessoa = primeira_pessoa.cor

        # Procura um carro ocupado que tenha a mesma cor da pessoa e que ainda tenha capacidade
        carro_encontrado = next((carro for carro in self.ocupadas.values()
                                 if carro.cor_carro == cor_pessoa and carro.ocupacao_atual < carro.capacidade), None)

        if carro_encontrado is None:
            # Nenhum carro disponível para essa cor
            return

        # Remove a pessoa da fila visível
        self.fila_visivel.pop(0)
        primeira_pessoa.hide()
        primeira_pessoa.deleteLater()

        # Incrementa a ocupação do carro
        carro_encontrado.ocupacao_atual += 1
        carro_encontrado.atualizar_ocupacao()

        # Atualiza o contador de pessoas restantes
        self.numero_aleatorio = max(0, self.numero_aleatorio - 1)
        self.numero_label.setText(str(self.numero_aleatorio))
        self.numero_label.adjustSize()

        # Se o carro estiver cheio, remove-o da tela e da lista de ocupados
        if carro_encontrado.ocupacao_atual == carro_encontrado.capacidade:
            carro_encontrado.hide()
            if hasattr(carro_encontrado, "animation"):
                carro_encontrado.animation.stop()
            pos = carro_encontrado.pos()
            self.ocupadas.pop((pos.x(), pos.y()), None)

        # Recarrega a fila visível até o máximo permitido, tirando da reserva
        while len(self.fila_visivel) < self.max_pessoas_fila and self.fila_reserva:
            imagem_path, cor = self.fila_reserva.pop(0)
            nova_pessoa = PessoaWidget(imagem_path, cor, parent=self.central_widget)
            nova_pessoa.show()
            self.fila_visivel.append(nova_pessoa)

        # Reposiciona as pessoas visíveis na fila, alinhadas horizontalmente
        for i, pessoa in enumerate(self.fila_visivel):
            pessoa.move(self.fila_start_x + i * self.fila_spacing_x, self.fila_start_y)

    def caminho_livre(self, carro_widget):
        # Verifica se o caminho para mover o carro está livre
        pos_atual = carro_widget.pos()
        x, y = pos_atual.x(), pos_atual.y()

        dx, dy = 0, 0
        # Define o deslocamento na direção que o carro está apontando
        if carro_widget.direcao == "up":
            dy = -70
        elif carro_widget.direcao == "down":
            dy = 70
        elif carro_widget.direcao == "left":
            dx = -70
        elif carro_widget.direcao == "right":
            dx = 70

        # Verifica se há algum carro bloqueando o caminho na direção do movimento
        while 0 <= x < 600 and 0 <= y < 800:
            x += dx
            y += dy

            for outro_carro in self.carros_widgets:
                if outro_carro is carro_widget:
                    continue
                # Se encontrar um carro na posição à frente, caminho não está livre
                if outro_carro.pos().x() == x and outro_carro.pos().y() == y:
                    return False

        # Se não encontrou obstáculos, caminho está livre
        return True
