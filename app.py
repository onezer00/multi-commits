import sys
import os
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QFileDialog, QLabel, QTextEdit,
                            QMessageBox, QCheckBox, QListWidget, QListWidgetItem, QSplitter, QTableWidget, QTableWidgetItem)
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
        self.projects_data = [] # Usaremos uma lista de dicionários ou objetos para guardar os dados dos projetos
        
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
        
        # Splitter horizontal para tabela de projetos e área de logs
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tabela de projetos
        self.table_projects = QTableWidget()
        self.table_projects.setColumnCount(4) # Projeto, Branch, Aplicar, Ação
        self.table_projects.setHorizontalHeaderLabels(["Projeto", "Branch", "Aplicar", "Ação"]) #Labels dos cabeçalhos
        self.splitter.addWidget(self.table_projects)
        
        # Área de log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.splitter.addWidget(self.log_area)
        
        self.splitter.setSizes([300, 500]) # Tamanhos iniciais
        layout.addWidget(self.splitter, 1)  # O "1" faz o splitter ocupar o espaço expansível
        
        # Botões de ação
        self.btn_execute = QPushButton("Copiar Arquivos") # Renomeado para refletir a ação inicial
        self.btn_execute.clicked.connect(self.execute_update)
        layout.addWidget(self.btn_execute)
        
        self.btn_confirm_commit = QPushButton("Confirmar Commit")
        self.btn_confirm_commit.setEnabled(False) # Desabilitado inicialmente
        self.btn_confirm_commit.clicked.connect(self.confirm_commits)
        layout.addWidget(self.btn_confirm_commit)

    def toggle_debug_mode(self, state):
        self.debug_mode = state == Qt.CheckState.Checked.value
        if self.debug_mode:
            self.log_message("Modo Debug ativado - Nenhum commit será realizado")
            self.btn_confirm_commit.setEnabled(False) # Desabilitar confirmar commit em debug
        else:
            self.log_message("Modo Debug desativado - Commits serão realizados normalmente")
            # Habilitar confirmar commit apenas se houver arquivos copiados e não houver erros de cópia graves
            if self.projects_data and all(proj.get("copy_status", "failed") != "failed" for proj in self.projects_data if proj.get("apply_checkbox", QCheckBox()).isChecked()):
                 self.btn_confirm_commit.setEnabled(True)
        
    def select_projects_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Selecionar Diretório de Projetos")
        if dir_path:
            self.projects_dir = dir_path
            # Mostrar apenas o nome do diretório selecionado
            self.lbl_projects.setText(f"Diretório selecionado: {os.path.basename(dir_path)}")
            self.populate_projects_table()
        
    def populate_projects_table(self):
        self.table_projects.setRowCount(0) # Limpa a tabela
        self.projects_data = []
        if not self.projects_dir:
            return
        for project_name in os.listdir(self.projects_dir):
            project_path = os.path.join(self.projects_dir, project_name)
            if os.path.isdir(project_path):
                try:
                    repo = Repo(project_path)
                    branch_name = repo.active_branch.name if not repo.bare else "N/A (Bare Repo)"
                except Exception:
                    branch_name = "Não é um repositório Git"
                    
                row_position = self.table_projects.rowCount()
                self.table_projects.insertRow(row_position)
                
                # Coluna Projeto
                self.table_projects.setItem(row_position, 0, QTableWidgetItem(project_name))
                
                # Coluna Branch
                self.table_projects.setItem(row_position, 1, QTableWidgetItem(branch_name))
                
                # Coluna Aplicar (Checkbox)
                apply_checkbox = QCheckBox()
                apply_checkbox.setChecked(True) # Marcado por padrão
                # Para centralizar o checkbox, precisamos de um widget container
                checkbox_container = QWidget()
                checkbox_layout = QVBoxLayout(checkbox_container)
                checkbox_layout.addWidget(apply_checkbox)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                checkbox_layout.setContentsMargins(0,0,0,0)
                self.table_projects.setCellWidget(row_position, 2, checkbox_container)
                
                # Coluna Ação (inicialmente vazia)
                action_widget = QWidget()
                action_layout = QVBoxLayout(action_widget)
                action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                action_layout.setContentsMargins(0,0,0,0)
                self.table_projects.setCellWidget(row_position, 3, action_widget)
                
                # Armazenar dados do projeto (Nome, Caminho, Repositório Git, etc)
                self.projects_data.append({
                    "name": project_name,
                    "path": project_path,
                    "branch": branch_name,
                    "apply_checkbox": apply_checkbox, # Referência ao checkbox para verificar estado
                    "action_layout": action_layout, # Referência ao layout para adicionar botões
                    "copy_status": "pending", # Status da cópia: pending, success, failed
                    "commit_status": "pending" # Status do commit: pending, success, failed, skipped
                })
        if not self.projects_data:
            self.log_message("Nenhum diretório de projeto encontrado no diretório selecionado.")
        
    def get_selected_projects_for_commit(self):
        selected_projects_data = []
        for project_data in self.projects_data:
            # Verificar se o checkbox está marcado E se a cópia foi bem sucedida para este projeto
            if project_data.get("apply_checkbox", QCheckBox()).isChecked() and project_data.get("copy_status") == "success":
                selected_projects_data.append(project_data)
        return selected_projects_data
        
    def select_update_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Atualização")
        if file_path:
            self.update_file = file_path
            # Mostrar caminho relativo se o diretório de projetos estiver selecionado
            if self.projects_dir:
                relative_path = os.path.relpath(file_path, self.projects_dir)
                self.lbl_update.setText(f"Arquivo selecionado: {relative_path}")
            else:
                self.lbl_update.setText(f"Arquivo selecionado: {file_path}") # Caminho completo se diretório não selecionado
            
    def select_target_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo Alvo")
        if file_path:
            self.target_file = file_path
            # Mostrar caminho relativo se o diretório de projetos estiver selecionado
            if self.projects_dir:
                relative_path = os.path.relpath(file_path, self.projects_dir)
                self.lbl_target.setText(f"Arquivo selecionado: {relative_path}")
            else:
                 self.lbl_target.setText(f"Arquivo selecionado: {file_path}") # Caminho completo se diretório não selecionado
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_area.append(f"[{timestamp}] {message}")
        
    def execute_update(self):
        if not all([self.projects_dir, self.update_file, self.target_file]):
            QMessageBox.warning(self, "Aviso", "Por favor, selecione todos os campos necessários.")
            return
            
        self.log_message("Iniciando processo de atualização (cópia de arquivos)...")
        
        success_copy = []
        failed_copy = []
        
        # Descobrir o projeto base a partir do arquivo alvo
        project_base = None
        for project_data in self.projects_data:
             project_path = project_data["path"]
             if os.path.isdir(project_path) and os.path.commonpath([os.path.abspath(self.target_file), os.path.abspath(project_path)]) == os.path.abspath(project_path):
                 project_base = project_path
                 break
        if not project_base:
            self.log_message("Não foi possível identificar o projeto base do arquivo alvo.")
            return
        # Calcular o caminho relativo do arquivo alvo em relação ao projeto base
        target_relative = os.path.relpath(self.target_file, project_base)
        
        # Iterar sobre todos os projetos listados (para cópia inicial)
        for project_data in self.projects_data:
            project_path = project_data["path"]
            target_path = os.path.join(project_path, target_relative)
            try:
                # Verificar se o arquivo alvo existe no projeto
                if os.path.exists(target_path):
                    # Copiar o arquivo de atualização
                    shutil.copy2(self.update_file, target_path)
                    project_data["copy_status"] = "success"
                    success_copy.append(target_path)
                    self.log_message(f"Arquivo copiado com sucesso para: {os.path.relpath(target_path, self.projects_dir)}")
                else:
                    project_data["copy_status"] = "failed"
                    failed_copy.append(target_path)
                    self.log_message(f"Arquivo alvo não encontrado no projeto: {os.path.relpath(target_path, self.projects_dir)}")
            except Exception as e:
                project_data["copy_status"] = "failed"
                failed_copy.append(target_path)
                self.log_message(f"Erro ao copiar arquivo para {os.path.relpath(target_path, self.projects_dir)}: {type(e).__name__}: {e}")
                
        self.log_message("\nProcesso de cópia finalizado. Por favor, revise e confirme os commits.")
        
        # Habilitar botão de confirmar commit se houver arquivos copiados com sucesso (e não estiver em debug)
        if success_copy and not self.debug_mode:
             self.btn_confirm_commit.setEnabled(True)

    def confirm_commits(self):
        selected_for_commit = self.get_selected_projects_for_commit()
        if not selected_for_commit:
            QMessageBox.warning(self, "Aviso", "Nenhum projeto selecionado para commit ou cópia falhou.")
            return
            
        self.log_message("\nIniciando processo de commit e push...")
        self.btn_confirm_commit.setEnabled(False) # Desabilitar botão enquanto commita
        
        success_commit = []
        failed_commit = []
        
        for project_data in selected_for_commit:
            project_path = project_data["path"]
            project_name = project_data["name"]
            target_relative = os.path.relpath(self.target_file, os.path.join(self.projects_dir, project_name))
            
            try:
                repo = Repo(project_path)
                repo.index.add([target_relative])
                
                # Verificar se há alterações para commitar
                if not repo.index.diff("HEAD") and not repo.untracked_files:
                    self.log_message(f"Nenhuma alteração para commitar no projeto: {project_name}")
                    project_data["commit_status"] = "skipped"
                    continue
                    
                commit = repo.index.commit(f"Atualização automática: {target_relative}")
                origin = repo.remote(name='origin')
                origin.push()
                branch_name = repo.active_branch.name
                self.log_message(f"Commit e push realizados com sucesso para: {project_name} ({commit.hexsha[:7]}) na branch: {branch_name}")
                project_data["commit_status"] = "success"
                project_data["last_commit_sha"] = commit.hexsha # Armazenar SHA para possível reversão
                success_commit.append(project_name)
                
                # Adicionar botão de reverter para este projeto
                revert_button = QPushButton("Reverter")
                revert_button.clicked.connect(lambda checked, data=project_data: self.revert_commit(data)) # Usar lambda para passar dados
                # Limpar layout da coluna Ação e adicionar o botão
                for i in reversed(range(project_data["action_layout"].count())): 
                    widget = project_data["action_layout"].itemAt(i).widget()
                    if widget is not None: widget.deleteLater()
                project_data["action_layout"].addWidget(revert_button)
                project_data["revert_button"] = revert_button
                
            except Exception as e:
                failed_commit.append(project_name)
                project_data["commit_status"] = "failed"
                self.log_message(f"Erro ao commitar/push no projeto {project_name}: {type(e).__name__}: {e}")

        # Gerar relatório final
        self.log_message("\n=== Relatório Final ===")
        self.log_message("\nArquivos copiados com sucesso:")
        for file in success_copy:
             self.log_message(f"- {os.path.relpath(file, self.projects_dir)}")
            
        self.log_message("\nArquivos com falha na cópia:")
        for file in failed_copy:
            self.log_message(f"- {os.path.relpath(file, self.projects_dir)}")
            
        self.log_message("\nProjetos commitados com sucesso:")
        for project in success_commit:
            self.log_message(f"- {project}")
            
        self.log_message("\nProjetos com falha no commit:")
        for project in failed_commit:
            self.log_message(f"- {project}")
            
        QMessageBox.information(self, "Processo Concluído", "Processo de atualização e commit finalizado!")

    def revert_commit(self, project_data):
        project_name = project_data["name"]
        project_path = project_data["path"]
        last_commit_sha = project_data.get("last_commit_sha")
        
        if not last_commit_sha:
            self.log_message(f"Nenhum commit encontrado para reverter no projeto: {project_name}")
            return

        confirm = QMessageBox.question(self, "Confirmar Reversão", 
                                       f"Tem certeza que deseja reverter o último commit no projeto '{project_name}' (SHA: {last_commit_sha[:7]})?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                       
        if confirm == QMessageBox.StandardButton.No:
            self.log_message(f"Reversão cancelada para o projeto: {project_name}")
            return
            
        self.log_message(f"Iniciando reversão para o projeto: {project_name}...")
        
        try:
            repo = Repo(project_path)
            # Use reset --hard para voltar ao commit anterior. Cuidado, isso descarta alterações locais.
            repo.git.reset('--hard', f'{last_commit_sha}~1')
            # Opcional: Forçar push para sobrescrever o commit remoto (use com cautela!)
            # origin = repo.remote(name='origin')
            # origin.push(repo.active_branch.name, force=True)
            
            self.log_message(f"Reversão bem sucedida para o projeto {project_name}. Retornado ao commit anterior a {last_commit_sha[:7]}.")
            # Desabilitar o botão de reverter após a ação (ou atualizar status)
            if project_data.get("revert_button"):
                 project_data["revert_button"].setEnabled(False)
                 project_data["revert_button"].setText("Revertido")
                 
        except Exception as e:
            self.log_message(f"Erro ao reverter commit no projeto {project_name}: {type(e).__name__}: {e}")
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MultiCommitsApp()
    window.show()
    sys.exit(app.exec()) 