import tkinter as tk
from tkinter import messagebox
import urllib.request
import urllib.error
import json
import os

FAVORITES_FILE = "favorites.json"

class GitHubFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("450x550")
        self.root.resizable(False, False)

        self.favorites = self.load_favorites()

        # --- Блок поиска ---
        tk.Label(root, text="Введите логин пользователя GitHub:", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        
        search_frame = tk.Frame(root)
        search_frame.pack(pady=5)
        
        self.entry_search = tk.Entry(search_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Найти", command=self.search_user, bg="#0366d6", fg="white").pack(side=tk.LEFT)

        # --- Результаты поиска ---
        tk.Label(root, text="Результаты поиска:", font=("Arial", 10)).pack(pady=(10, 0))
        self.listbox_results = tk.Listbox(root, width=50, height=8, selectmode=tk.SINGLE)
        self.listbox_results.pack(pady=5)

        tk.Button(root, text="Добавить в избранное ⭐️", command=self.add_to_favorites, bg="#2ea44f", fg="white").pack(pady=5)

        # --- Разделитель ---
        tk.Frame(root, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, padx=20, pady=10)

        # --- Избранное ---
        tk.Label(root, text="Избранные пользователи:", font=("Arial", 10, "bold")).pack()
        self.listbox_favorites = tk.Listbox(root, width=50, height=8, selectmode=tk.SINGLE)
        self.listbox_favorites.pack(pady=5)
        
        tk.Button(root, text="Удалить из избранного", command=self.remove_from_favorites, bg="#cb2431", fg="white").pack(pady=5)

        self.update_favorites_listbox()

    # --- Работа с данными (JSON) ---
    def load_favorites(self):
        if not os.path.exists(FAVORITES_FILE):
            return []
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def save_favorites(self):
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    # --- Логика API и валидация ---
    def search_user(self):
        query = self.entry_search.get().strip()
        
        # 5. Проверка корректности ввода (поле не пустое)
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не может быть пустым!")
            return

        self.listbox_results.delete(0, tk.END)
        
        # Запрос к GitHub API
        url = f"https://api.github.com/search/users?q={query}&per_page=10"
        
        try:
            # Используем User-Agent, так как GitHub API требует его наличия
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode('utf-8'))
            
            users = data.get("items", [])
            if not users:
                self.listbox_results.insert(tk.END, "Пользователи не найдены.")
                return
                
            for user in users:
                self.listbox_results.insert(tk.END, user['login'])
                
        except urllib.error.URLError as e:
            messagebox.showerror("Ошибка сети", f"Не удалось подключиться к API GitHub.\n{e}")

    # --- Логика интерфейса ---
    def add_to_favorites(self):
        selected_indices = self.listbox_results.curselection()
        if not selected_indices:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя из результатов поиска.")
            return
            
        username = self.listbox_results.get(selected_indices[0])
        
        if username == "Пользователи не найдены.":
            return
            
        if username not in self.favorites:
            self.favorites.append(username)
            self.save_favorites()
            self.update_favorites_listbox()
            messagebox.showinfo("Успех", f"Пользователь {username} добавлен в избранное!")
        else:
            messagebox.showinfo("Внимание", f"Пользователь {username} уже есть в избранном.")

    def remove_from_favorites(self):
        selected_indices = self.listbox_favorites.curselection()
        if not selected_indices:
            messagebox.showwarning("Внимание", "Выберите пользователя из избранного для удаления.")
            return
            
        username = self.listbox_favorites.get(selected_indices[0])
        self.favorites.remove(username)
        self.save_favorites()
        self.update_favorites_listbox()

    def update_favorites_listbox(self):
        self.listbox_favorites.delete(0, tk.END)
        for user in self.favorites:
            self.listbox_favorites.insert(tk.END, user)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubFinderApp(root)
    root.mainloop()
