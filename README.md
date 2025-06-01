# 🚀 Multi Commits

![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> **Ferramenta gráfica para atualizar arquivos em múltiplos projetos Git de forma rápida, segura e automatizada.**

---

## ✨ Funcionalidades

- ✅ **Interface gráfica intuitiva** para seleção de diretórios e arquivos
- ✅ **Seleção de múltiplos projetos** para atualização (checkbox)
- ✅ **Atualização automática** de arquivos em vários projetos
- ✅ **Commit e push automático** das alterações
- ✅ **Relatório detalhado** das operações realizadas
- ✅ **Logs de erro detalhados** (tipo e mensagem da exceção)
- ✅ **Modo Debug** para testar atualizações sem realizar commits

---

## 🖥️ Pré-requisitos

- Python **3.8** ou superior
- Git instalado e configurado
- Dependências Python listadas em `requirements.txt`

---

## ⚡ Instalação

```bash
git clone https://github.com/seu-usuario/multi-commits.git
cd multi-commits
pip install -r requirements.txt
```

---

## 🛠️ Como usar

1. Execute o script:
   ```bash
   python multi_commits.py
   ```
2. Na interface gráfica:
   - 📁 Selecione o diretório onde estão os projetos
   - ☑️ Marque/desmarque os projetos que deseja atualizar
   - 📄 Selecione o arquivo que servirá como atualização
   - 📄 Selecione o arquivo alvo em um dos projetos  
     <sub><sup>*(Os outros projetos precisam ter uma estrutura igual à selecionada)*</sup></sub>
   - 🐞 (Opcional) Ative o **Modo Debug** se desejar testar sem fazer commits
   - ▶️ Clique em **Executar Atualização**

---

## 📋 O que acontece?

- Os arquivos selecionados são atualizados nos projetos marcados
- Commits e push são realizados automaticamente (exceto no modo debug)
- Um relatório detalhado é exibido na interface
- Logs de erro mostram o tipo e a mensagem da exceção, facilitando o diagnóstico

---

## 🐞 Modo Debug

> Permite testar as atualizações sem realizar commits no Git.

- Os arquivos são atualizados normalmente
- Nenhum commit ou push é realizado
- O log mostra claramente que está em modo Debug

---

## 📁 Estrutura dos Projetos

Os projetos devem seguir a mesma estrutura de diretórios para que a atualização funcione corretamente.  
O arquivo alvo deve estar no mesmo caminho relativo em todos os projetos.

---

## 🔒 Segurança

- Todas as operações são registradas em log
- Modo Debug disponível para testes seguros
- **Não** são criados arquivos de backup manualmente, pois o Git já garante o histórico de alterações

---

## 🤝 Contribuição

Contribuições são bem-vindas!  
Abra uma issue ou envie um pull request para sugerir melhorias.

---

## 📄 Licença

Este projeto está licenciado sob a MIT License.  
Veja o arquivo [LICENSE](LICENSE) para detalhes. 