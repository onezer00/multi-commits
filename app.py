import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QFileDialog, QLabel, QTextEdit,
                            QMessageBox, QCheckBox, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from git import Repo, GitCommandError
import traceback

class MultiCommitsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi Commits - Atualizador de Projetos")
        self.setGeometry(100, 100, 800, 600)
        
        # Variáveis para armazenar os caminhos selecionados
        self.projects_dir = ""
        self.update_file = ""
        self.target_file = ""
        self.debug_mode = False
        self.projects_list = []
        
        # Configuração da interface
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Botão para selecionar diretório de projetos
        self.btn_projects = QPushButton("Selecionar Diretório de Projetos")
        self.btn_projects.clicked.connect(self.select_projects_dir)
        layout.addWidget(self.btn_projects)
        
        # Label para mostrar diretório selecionado
        self.lbl_projects = QLabel("Nenhum diretório selecionado")
        layout.addWidget(self.lbl_projects)
        
        # Lista de projetos com checkboxes
        self.list_projects = QListWidget()
        self.list_projects.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        layout.addWidget(self.list_projects)
        self.list_projects.setMaximumHeight(120)
        
        # Botão para selecionar arquivo de atualização
        self.btn_update = QPushButton("Selecionar Arquivo de Atualização")
        self.btn_update.clicked.connect(self.select_update_file)
        layout.addWidget(self.btn_update)
        
        # Label para mostrar arquivo de atualização
        self.lbl_update = QLabel("Nenhum arquivo selecionado")
        layout.addWidget(self.lbl_update)
        
        # Botão para selecionar arquivo alvo
        self.btn_target = QPushButton("Selecionar Arquivo Alvo")
        self.btn_target.clicked.connect(self.select_target_file)
        layout.addWidget(self.btn_target)
        
        # Label para mostrar arquivo alvo
        self.lbl_target = QLabel("Nenhum arquivo selecionado")
        layout.addWidget(self.lbl_target)
        
        # Checkbox para modo debug
        self.chk_debug = QCheckBox("Modo Debug (sem commit)")
        self.chk_debug.stateChanged.connect(self.toggle_debug_mode)
        layout.addWidget(self.chk_debug)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        # Botão para executar atualização
        self.btn_execute = QPushButton("Executar Atualização")
        self.btn_execute.clicked.connect(self.execute_update)
        layout.addWidget(self.btn_execute)
        
    def toggle_debug_mode(self, state):
        self.debug_mode = state == Qt.CheckState.Checked.value
        if self.debug_mode:
            self.log_message("Modo Debug ativado - Nenhum commit será realizado")
        else:
            self.log_message("Modo Debug desativado - Commits serão realizados normalmente")
        
    def select_projects_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Projetos")
        if dir_path:
            self.projects_dir = dir_path
            self.lbl_projects.setText(f"Diretório selecionado: {dir_path}")
            self.populate_projects_list()
        
    def populate_projects_list(self):
        self.list_projects.clear()
        self.projects_list = []
        if not self.projects_dir:
            return
        for project in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, project)
            if os.path.isdir(project_path):
                item = QListWidgetItem(project)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                self.list_projects.addItem(item)
                self.projects_list.append(project)
        if not self.projects_list:
            self.log_message("Nenhum projeto encontrado no diretório selecionado.")
        
    def get_selected_projects(self):
        selected = []
        for i in range(self.list_projects.count()):
            item = self.list_projects.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
        
    def select_update_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Atualização")
        if file_path:
            self.update_file = file_path
            self.lbl_update.setText(f"Arquivo selecionado: {file_path}")
            
    def select_target_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo Alvo")
        if file_path:
            self.target_file = file_path
            self.lbl_target.setText(f"Arquivo selecionado: {file_path}")
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        
    def execute_update(self):
        if not all([self.projects_dir, self.update_file, self.target_file]):
            QMessageBox.warning(self, "Aviso", "Por favor, selecione todos os campos necessários.")
            return
        selected_projects = self.get_selected_projects()
        if not selected_projects:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um projeto para atualizar.")
            return
        self.log_message("Iniciando processo de atualização...")
        if self.debug_mode:
            self.log_message("MODO DEBUG: Nenhum commit será realizado")
        
        # Lista para armazenar resultados
        success_files = []
        failed_files = []
        
        # Descobrir o projeto base a partir do arquivo alvo
        project_base = None
        for project in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, project)
            if os.path.isdir(project_path) and os.path.commonpath([os.path.abspath(self.target_file), os.path.abspath(project_path)]) == os.path.abspath(project_path):
                project_base = project_path
                break
        if not project_base:
            self.log_message("Não foi possível identificar o projeto base do arquivo alvo.")
            return
        # Calcular o caminho relativo do arquivo alvo em relação ao projeto base
        target_relative = os.path.relpath(self.target_file, project_base)
        
        # Iterar apenas sobre os projetos selecionados
        for project in selected_projects:
            project_path = os.path.join(self.projects_dir, project)
            if os.path.isdir(project_path):
                target_path = os.path.join(project_path, target_relative)
                try:
                    # Verificar se o arquivo alvo existe no projeto
                    if os.path.exists(target_path):
                        # Copiar o arquivo de atualização
                        shutil.copy2(self.update_file, target_path)
                        
                        if not self.debug_mode:
                            # Fazer commit e push apenas se não estiver em modo debug
                            repo = Repo(project_path)
                            repo.index.add([target_relative])
                            repo.index.commit(f"Atualização automática: {target_relative}")
                            origin = repo.remote(name='origin')
                            origin.push()
                            self.log_message(f"Commit e push realizados para: {target_path}")
                        else:
                            self.log_message(f"[DEBUG] Arquivo atualizado (sem commit): {target_path}")
                        
                        success_files.append(target_path)
                        self.log_message(f"Arquivo atualizado com sucesso: {target_path}")
                    else:
                        failed_files.append(target_path)
                        self.log_message(f"Arquivo não encontrado: {target_path}")
                except Exception as e:
                    failed_files.append(target_path)
                    self.log_message(f"Erro ao atualizar {target_path}: {type(e).__name__}: {e}")
        # Gerar relatório
        self.log_message("\n=== Relatório de Atualização ===")
        self.log_message("\nArquivos atualizados com sucesso:")
        for file in success_files:
            self.log_message(f"- {file}")
        self.log_message("\nArquivos com falha:")
        for file in failed_files:
            self.log_message(f"- {file}")
        if self.debug_mode:
            self.log_message("\nMODO DEBUG: Nenhum commit foi realizado")
        QMessageBox.information(self, "Concluído", "Processo de atualização finalizado!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiCommitsApp()
    window.show()
    sys.exit(app.exec()) 