# command.py
# Este arquivo implementa o padrão de design Command, que encapsula ações como objetos, permitindo desfazer e refazer operações.
# Ele inclui uma classe base abstrata para comandos e implementações específicas para gerenciar tarefas.

from abc import ABC, abstractmethod

# Classe base abstrata para comandos
class Command(ABC):
    """Define a interface para comandos com métodos para executar (do) e desfazer (undo)."""
    @abstractmethod
    def do(self): ...  # Método para executar o comando

    @abstractmethod
    def undo(self): ...  # Método para desfazer o comando

# Gerenciador de comandos para controle de desfazer/refazer
class CommandManager:
    def __init__(self):
        """Inicializa as pilhas de comandos para desfazer e refazer."""
        self._undo = []  # Pilha de comandos executados
        self._redo = []  # Pilha de comandos desfeitos

    def do(self, cmd: 'Command'):
        """Executa um comando e o adiciona à pilha de desfazer."""
        cmd.do()  # Executa o comando
        self._undo.append(cmd)  # Adiciona à pilha de desfazer
        self._redo.clear()  # Limpa a pilha de refazer

    def undo(self):
        """Desfaz o último comando executado."""
        if not self._undo: return  # Verifica se há comandos para desfazer
        c = self._undo.pop()  # Remove o último comando da pilha de desfazer
        c.undo()  # Desfaz o comando
        self._redo.append(c)  # Adiciona à pilha de refazer

    def redo(self):
        """Refaz o último comando desfeito."""
        if not self._redo: return  # Verifica se há comandos para refazer
        c = self._redo.pop()  # Remove o último comando da pilha de refazer
        c.do()  # Reexecuta o comando
        self._undo.append(c)  # Adiciona novamente à pilha de desfazer

# Comando para adicionar uma nova tarefa
class AddTask(Command):
    def __init__(self, repo, title, priority=2, tags=None, scheduled=None):
        """Inicializa o comando com os dados da nova tarefa."""
        self.repo = repo  # Repositório de tarefas
        self.kw = dict(title=title, priority=priority, tags=tags, scheduled=scheduled)  # Dados da tarefa
        self.created = None  # Referência à tarefa criada

    def do(self):
        """Cria a nova tarefa no repositório."""
        self.created = self.repo.add(**self.kw)

    def undo(self):
        """Remove a tarefa criada."""
        self.repo.remove(self.created.id)

# Comando para editar uma tarefa existente
class EditTask(Command):
    def __init__(self, repo, tid, fields):
        """Inicializa o comando com os dados da tarefa a ser editada."""
        self.repo = repo  # Repositório de tarefas
        self.tid = tid  # ID da tarefa a ser editada
        self.fields = fields  # Campos a serem atualizados
        self.prev = None  # Armazena os valores anteriores para desfazer

    def do(self):
        """Atualiza os campos da tarefa no repositório."""
        t = self.repo.get(self.tid)  # Obtém a tarefa
        self.prev = {k: getattr(t, k) for k in self.fields}  # Salva os valores anteriores
        self.repo.update(self.tid, **self.fields)  # Atualiza a tarefa

    def undo(self):
        """Restaura os valores anteriores da tarefa."""
        self.repo.update(self.tid, **self.prev)

# Comando para excluir uma tarefa
class DeleteTask(Command):
    def __init__(self, repo, tid):
        """Inicializa o comando com o ID da tarefa a ser excluída."""
        self.repo = repo  # Repositório de tarefas
        self.tid = tid  # ID da tarefa
        self.prev = None  # Armazena os dados da tarefa para desfazer

    def do(self):
        """Remove a tarefa do repositório."""
        t = self.repo.get(self.tid)  # Obtém a tarefa
        self.prev = t.to_dict()  # Salva os dados da tarefa
        self.repo.remove(self.tid)  # Remove a tarefa

    def undo(self):
        """Restaura a tarefa removida."""
        from models import Task
        obj = Task.from_dict(self.prev)  # Reconstrói a tarefa
        self.repo.tasks.append(obj)  # Adiciona de volta ao repositório
        self.repo._save()  # Salva as alterações

# Comando para alternar o estado de conclusão de uma tarefa
class ToggleDone(Command):
    def __init__(self, repo, tid, stats=None):
        """Inicializa o comando com o ID da tarefa e estatísticas opcionais."""
        self.repo = repo  # Repositório de tarefas
        self.tid = tid  # ID da tarefa
        self.prev = None  # Armazena o estado anterior
        self.stats = stats  # Estatísticas opcionais

    def do(self):
        """Alterna o estado de conclusão da tarefa."""
        t = self.repo.get(self.tid)  # Obtém a tarefa
        self.prev = t.done  # Salva o estado anterior
        self.repo.update(self.tid, done=not t.done)  # Alterna o estado
        if not self.prev and self.stats:
            self.stats.inc_done_today(1)  # Incrementa estatísticas se a tarefa foi concluída

    def undo(self):
        """Restaura o estado anterior da tarefa."""
        # Não decrementa estatísticas ao desfazer para simplificar
        self.repo.update(self.tid, done=self.prev)