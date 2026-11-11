import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from pypdf import PdfReader, PdfWriter

class App:
    def __init__(self, root):
        self.root = root
        root.title("PDF Unificador")
        root.geometry("720x470")
        root.minsize(540, 350)
        self.files = []
        ttk.Label(root, text="PDF Unificador", font=("Segoe UI", 19, "bold")).pack(pady=(18, 4))
        ttk.Label(root, text="Selecione os documentos, organize a ordem e una em um único PDF.").pack(pady=(0, 12))
        frame = ttk.Frame(root)
        frame.pack(fill="both", expand=True, padx=20)
        self.listbox = tk.Listbox(frame, selectmode=tk.EXTENDED, font=("Segoe UI", 11))
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(frame, orient="vertical", command=self.listbox.yview)
        scroll.pack(side="left", fill="y")
        self.listbox.configure(yscrollcommand=scroll.set)
        side = ttk.Frame(frame)
        side.pack(side="left", fill="y", padx=(12, 0))
        for label, action in [("Adicionar PDFs", self.add), ("Remover", self.remove), ("Subir", lambda: self.move(-1)), ("Descer", lambda: self.move(1)), ("Limpar lista", self.clear)]:
            ttk.Button(side, text=label, command=action, width=17).pack(pady=4)
        self.status = tk.StringVar(value="Nenhum documento selecionado.")
        ttk.Label(root, textvariable=self.status).pack(pady=8)
        ttk.Button(root, text="UNIR PDFs E SALVAR", command=self.merge).pack(pady=(0, 18), ipadx=35, ipady=8)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for i, file in enumerate(self.files, 1):
            self.listbox.insert(tk.END, f"{i:02d}  {Path(file).name}")
        self.status.set(f"{len(self.files)} documento(s) na lista.")

    def add(self):
        paths = filedialog.askopenfilenames(title="Selecionar PDFs", filetypes=[("Arquivos PDF", "*.pdf")])
        for path in paths:
            if path not in self.files:
                self.files.append(path)
        self.refresh()

    def remove(self):
        for i in reversed(self.listbox.curselection()):
            self.files.pop(i)
        self.refresh()

    def clear(self):
        self.files.clear()
        self.refresh()

    def move(self, step):
        selected = self.listbox.curselection()
        if len(selected) != 1:
            messagebox.showinfo("Ordenação", "Selecione apenas um documento para mover.")
            return
        i = selected[0]
        j = i + step
        if 0 <= j < len(self.files):
            self.files[i], self.files[j] = self.files[j], self.files[i]
            self.refresh()
            self.listbox.selection_set(j)
            self.listbox.see(j)

    def merge(self):
        if len(self.files) < 2:
            messagebox.showwarning("PDF Unificador", "Adicione pelo menos dois arquivos PDF.")
            return
        target = filedialog.asksaveasfilename(title="Salvar PDF unificado", defaultextension=".pdf", filetypes=[("Arquivos PDF", "*.pdf")], initialfile="PDF_Unificado.pdf")
        if not target:
            return
        if any(Path(target).resolve() == Path(source).resolve() for source in self.files):
            messagebox.showerror("Proteção", "O destino não pode substituir um PDF original.")
            return
        writer = PdfWriter()
        try:
            for source in self.files:
                reader = PdfReader(source)
                if reader.is_encrypted:
                    raise ValueError(f"Arquivo protegido por senha: {Path(source).name}")
                writer.append(reader)
            with open(target, "wb") as output:
                writer.write(output)
        except Exception as exc:
            try:
                Path(target).unlink(missing_ok=True)
            except OSError:
                pass
            messagebox.showerror("Falha ao unir", str(exc))
            return
        finally:
            writer.close()
        messagebox.showinfo("Concluído", f"PDF criado com sucesso!\\n{target}")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
