import tkinter as tk
from tkinter import filedialog, messagebox
import re

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de Sentencias MongoDB")
        
        self.editor = tk.Text(self, wrap="word")
        self.editor.pack(fill="both", expand=True)
        
        self.create_menu()
        self.create_error_area()
        
        self.parser = MongoDBParser()
        
    def create_menu(self):
        menubar = tk.Menu(self)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Nuevo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_command(label="Guardar Como", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        analysis_menu = tk.Menu(menubar, tearoff=0)
        analysis_menu.add_command(label="Generar sentencias MongoDB", command=self.generate_mongodb_statements)
        menubar.add_cascade(label="Análisis", menu=analysis_menu)
        
        tokens_menu = tk.Menu(menubar, tearoff=0)
        tokens_menu.add_command(label="Ver Tokens", command=self.show_tokens)
        menubar.add_cascade(label="Tokens", menu=tokens_menu)
        
        self.config(menu=menubar)
        
    def create_error_area(self):
        self.error_area = tk.Text(self, wrap="word", height=5)
        self.error_area.pack(fill="both", expand=True)
        
    def new_file(self):
        self.editor.delete("1.0", tk.END)
        
    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.editor.delete("1.0", tk.END)
                self.editor.insert(tk.END, content)
                
    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as file:
                content = self.editor.get("1.0", tk.END)
                file.write(content)
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            with open(file_path, "w") as file:
                content = self.editor.get("1.0", tk.END)
                file.write(content)
    
    def generate_mongodb_statements(self):
        
        code = self.editor.get("1.0", tk.END)
        
        
        self.parser.parse(code)
        
        
        if self.parser.errors:
            
            self.error_area.delete("1.0", tk.END)
            for error in self.parser.errors:
                self.error_area.insert(tk.END, f"{error['type']}: Línea {error['line']}: {error['description']}\n")
        else:
            
            self.error_area.delete("1.0", tk.END)
            
            
            if self.parser.statements:
                
                for statement in self.parser.statements:
                    messagebox.showinfo("Sentencia Generada", statement)
            else:
                
                messagebox.showinfo("No se Generaron Sentencias", "No se generaron sentencias de MongoDB.")

       
        
    def show_tokens(self):
        code = self.editor.get("1.0", tk.END)
        tokens = self.tokenize(code)
       
        tokens_window = tk.Toplevel(self)
        tokens_window.title("Tokens Reconocidos")

        
        tokens_text = tk.Text(tokens_window)
        tokens_text.pack(fill="both", expand=True)

        
        tokens_text.insert(tk.END, "Número correlativo\tToken\tNúmero de Token\tLexema\n")
        for i, token in enumerate(tokens, start=1):
            tokens_text.insert(tk.END, f"{i}\t{token['type']}\t{token['number']}\t{token['lexeme']}\n")

    def tokenize(self, code):
        tokens = []
        
        token_patterns = [
            (r'(CrearBD|EliminarBD|CrearColeccion|EliminarColeccion|InsertarUnico|ActualizarUnico|EliminarUnico|BuscarTodo|BuscarUnico)', 'Funcion'),
            (r'("[^"]*"|\w+)', 'Lexema')  
        ]

        
        for line_number, line in enumerate(code.split('\n'), start=1):
            
            for pattern, token_type in token_patterns:
                
                for match in re.finditer(pattern, line):
                    lexeme = match.group()
                    start = match.start()
                    end = match.end()
                    
                    tokens.append({
                        'type': token_type,
                        'number': line_number,
                        'lexeme': lexeme,
                        'start': start,
                        'end': end
                    })

        return tokens

class MongoDBParser:
    def __init__(self):
        self.statements = []
        self.errors = []

    def parse(self, code):
        self.errors = []
        self.statements = []

        lines = code.split('\n')
        for line_number, line in enumerate(lines, start=1):
            if line.strip().startswith('---') or line.strip().startswith('/*'):
                continue

            self.parse_line(line, line_number)

    def parse_line(self, line, line_number):
        match = re.match(r'^CrearBD (\w+)', line)
        if match:
            db_name = match.group(1)
            mongo_statement = f'use("{db_name}")'
            self.statements.append(mongo_statement)
        else:
            self.errors.append({
                'type': 'Sintáctico',
                'line': line_number,
                'description': f"No se reconoce el comando en la línea {line_number}: {line}"
            })

if __name__ == "__main__":
    app = App()
    app.mainloop()
