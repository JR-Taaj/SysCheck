import os
import sqlite3
import tkinter
import customtkinter
from PIL import ImageTk, Image
import textwrap

# Configuration de l'apparence
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("green")

DB_PATH = "./data/users.db"


def initialize_database():
    os.makedirs("./data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entreprise TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            notes
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin"))
    conn.commit()
    conn.close()

def validate_credentials(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    result = cursor.fetchone()
    conn.close()
    return result is not None

class MPlusApp(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("MPlus")
        self.geometry("600x440")
        self.is_fullscreen = True
        self._show_login_page()
        self.attributes('-fullscreen', True)

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Return>", self._on_enter_press)

    
    def toggle_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.attributes('-fullscreen', False)
            self.center_window(600, 440)
        else:
            self.attributes('-fullscreen', True)
        self.is_fullscreen = not self.is_fullscreen

    def center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        self.geometry(f'{width}x{height}+{position_right}+{position_top}')

    def _show_login_page(self):
        self._clear_window()

        background_image = ImageTk.PhotoImage(Image.open("./assets/papa.png"))
        self.background_label = customtkinter.CTkLabel(self, image=background_image, text="")
        self.background_label.image = background_image
        self.background_label.pack()

        self.login_frame = customtkinter.CTkFrame(master=self.background_label, width=320, height=360, corner_radius=30)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        title_label = customtkinter.CTkLabel(master=self.login_frame, text="         Connexion", font=("Century Gothic", 20))
        title_label.place(x=50, y=45)

        self.username_entry = customtkinter.CTkEntry(master=self.login_frame, width=220, placeholder_text="Nom d'utilisateur")
        self.username_entry.place(x=50, y=110)

        self.password_entry = customtkinter.CTkEntry(master=self.login_frame, width=220, placeholder_text="Mot de passe", show="*")
        self.password_entry.place(x=50, y=165)

        forgot_password_label = customtkinter.CTkLabel(master=self.login_frame, text="Mot de passe oublié ?", font=("Century Gothic", 12))
        forgot_password_label.place(x=155, y=195)

        login_button = customtkinter.CTkButton(master=self.login_frame, width=220, text="Se connecter", command=self._on_login, corner_radius=6)
        login_button.place(x=50, y=240)

    def _on_enter_press(self, event=None):
        self._on_login()

    def _on_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if validate_credentials(username, password):
            self.current_username = username
            self._show_home_page()
        else:
            error = customtkinter.CTkLabel(master=self.login_frame, text="       Identifiants incorrects", text_color="red", font=("Arial", 12))
            error.place(x=80, y=280)
    def _filter_clients(self, event=None):
        search_text = self.search_entry.get().lower()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT entreprise, email, phone, notes FROM clients")
        clients = cursor.fetchall()
        conn.close()

        filtered = [client for client in clients if any(search_text in (str(field).lower() if field else "") for field in client)]

        # Supprime l'ancien tableau et recrée le tableau avec les résultats filtrés
        self._update_table(filtered)
    def _update_table(self, clients_data):
        if hasattr(self, 'tableau_frame'):
            self.tableau_frame.destroy()

        self.tableau_frame = customtkinter.CTkScrollableFrame(self, width=1300, height=500)
        self.tableau_frame.place(x=230, y=150)

        headers = ["Entreprise", "Email", "Téléphone", "Notes"]
        for col_index, header in enumerate(headers):
            header_label = customtkinter.CTkLabel(
                self.tableau_frame,
                text=header,
                font=("Century Gothic", 14, "bold"),
                text_color="#13B05F",
                width=250,
                anchor="w"
            )
            header_label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")

        for row_index, client in enumerate(clients_data, start=1):
            for col_index, value in enumerate(client):
                # Si la valeur est trop longue, le texte sera automatiquement renvoyé à la ligne
                cell_label = customtkinter.CTkLabel(
                    self.tableau_frame,
                    text=value if value else "Non renseigné",  # Afficher un message si la valeur est vide
                    font=("Century Gothic", 12),
                    width=250,
                    anchor="w",
                    wraplength=250  # Limite la largeur du texte et permet un retour à la ligne
                )
                cell_label.grid(row=row_index, column=col_index, padx=10, pady=5, sticky="w")

    def _show_home_page(self):
        self._clear_window()
        self.bind("<Button-1>", self._defocus_search_entry_on_click)
        self.bind("<Escape>", self._defocus_search_entry)
        logo_image = Image.open("./assets/logo.png")
        logo_image = logo_image.resize((40, 40))
        logo_photo = ImageTk.PhotoImage(logo_image)

        title_label = customtkinter.CTkLabel(self, text="Gestion entreprise", font=("Century Gothic", 25, "bold"), text_color="#808080", image=logo_photo, compound="left", padx=20)
        title_label.image = logo_photo
        title_label.place(x=180, y=23)

        logo_user = Image.open("./assets/user.png")
        logo_user = logo_user.resize((40, 40))
        logo_pics = ImageTk.PhotoImage(logo_user)

        self.user_button_image = logo_pics  # Pour éviter que l'image soit supprimée par le GC

        self.user_button = customtkinter.CTkButton(
            self,
            text=self.current_username,
            image=self.user_button_image,
            compound="left",
            width=180,
            height=40,
            fg_color="transparent",
            hover_color="#222222",
            text_color="#13B05F",
            font=("Century Gothic", 14, "bold"),
            command=self._show_user_menu
        )
        self.user_button.place(relx=1.0, x=-100, y=20, anchor="ne")

        # Texte Client
        clients_label = customtkinter.CTkLabel(
            self,
            text="Clients",
            font=("Century Gothic", 25, "bold"), 
            text_color="white"
        )
        clients_label.place(x=200, y=100)

        # Placeholder de Recherche
        self.search_entry = customtkinter.CTkEntry(
            self,
            placeholder_text="Rechercher un client...",
            width=900,
            height=35
        )
        self.search_entry.bind("<Return>", self._filter_clients)
        self.search_entry.place(x=370, y=100)

        # Texte Filtrer
        logo_image2 = Image.open("./assets/filter.png")
        logo_image2 = logo_image2.resize((25, 25))
        logo_photo2 = ImageTk.PhotoImage(logo_image2)

        filter_label = customtkinter.CTkLabel(
            self,
            text="Filtrer",
            font=("Century Gothic", 14, "bold"),
            text_color="grey",
            image=logo_photo2, 
            compound="left", 
            padx=10
        )
        filter_label.image = logo_photo2
        filter_label.place(x=1270, y=105)

        # Bouton "Ajouter un client"
        add_button = customtkinter.CTkButton(
            self,
            text="Ajouter un client",
            fg_color="#1473E6",
            hover_color="#1429E6",
            text_color="white",
            corner_radius=9,
            width=160,
            height=35,
            command=self._show_add_client_form  # C'est ici qu'on associe la fonction d'affichage
        )
        add_button.place(x=1400, y=100)

        line_frame = customtkinter.CTkFrame(self, height=3, width=self.winfo_width(), fg_color="#2f2f2f")
        line_frame.place(x=0, y=70)

        shadow_frame = customtkinter.CTkFrame(self, height=3, width=self.winfo_width(), fg_color="#a0a0a0")  # Gris clair pour ombre
        shadow_frame.place(x=0, y=73)

        tableau_frame = customtkinter.CTkScrollableFrame(self, width=1300, height=500)
        tableau_frame.place(x=230, y=150)

        headers = ["Entreprise", "Email", "Téléphone", "Notes"]
        for col_index, header in enumerate(headers):
            header_label = customtkinter.CTkLabel(
                tableau_frame,
                text=header,
                font=("Century Gothic", 14, "bold"),
                text_color="#13B05F",
                width=250,
                anchor="w",
                wraplength=250
            )
            header_label.grid(row=0, column=col_index, padx=10, pady=10, sticky="w")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT entreprise, email, phone, notes FROM clients")
        clients = cursor.fetchall()
        conn.close()

        for row_index, client in enumerate(clients, start=1):
            entreprise, email, phone, notes = client
            for col_index, value in enumerate(client):
                cell_label = customtkinter.CTkLabel(
                    tableau_frame,
                    text=value if value else "",
                    font=("Century Gothic", 12),
                    width=250,
                    anchor="w",
                    wraplength=250
                )
                cell_label.grid(row=row_index, column=col_index, padx=10, pady=5, sticky="w")

            # Ajouter les boutons Modifier et Supprimer
            

            modify_button = customtkinter.CTkButton(
                tableau_frame,
                text="Modifier",
                width=80,
                height=25,
                fg_color="#E6B800",
                text_color="black",
                font=("Century Gothic", 11, "bold"),
                command=lambda e=entreprise, em=email, p=phone, n=notes: self._show_edit_client_form(e, em, p, n)
            )
            modify_button.grid(row=row_index, column=4, padx=(5, 2), pady=5)

            delete_button = customtkinter.CTkButton(
                tableau_frame,
                text="Supprimer",
                width=80,
                height=25,
                fg_color="#E61414",
                text_color="white",
                font=("Century Gothic", 11, "bold"),
                command=lambda e=entreprise: self._delete_client(e)
            )
            delete_button.grid(row=row_index, column=5, padx=(2, 10), pady=5)
    
    def _show_add_client_form(self):
        self._clear_window()

        title = customtkinter.CTkLabel(self, text="Ajouter un client", font=("Century Gothic", 24, "bold"))
        title.pack(pady=30)

        self.entry_entreprise = customtkinter.CTkEntry(self, placeholder_text="Nom de l'entreprise", width=400)
        self.entry_entreprise.pack(pady=10)

        self.entry_email = customtkinter.CTkEntry(self, placeholder_text="Email", width=400)
        self.entry_email.pack(pady=10)

        self.entry_phone = customtkinter.CTkEntry(self, placeholder_text="Numéro de téléphone", width=400)
        self.entry_phone.pack(pady=10)

        self.entry_notes = customtkinter.CTkEntry(self, placeholder_text="Notes", width=400)
        self.entry_notes.pack(pady=10)

        save_button = customtkinter.CTkButton(
            self,
            text="Enregistrer",
            fg_color="#13B05F",
            hover_color="#0e8a4d",
            width=200,
            command=self._save_client
        )
        save_button.pack(pady=20)

        cancel_button = customtkinter.CTkButton(
            self,
            text="Annuler",
            fg_color="gray",
            hover_color="darkgray",
            width=200,
            command=self._show_home_page
        )
        cancel_button.pack()

    def _save_client(self):
        entreprise = self.entry_entreprise.get()
        email = self.entry_email.get()
        phone = self.entry_phone.get()
        notes = self.entry_notes.get()

        if entreprise:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients (entreprise, email, phone, notes) VALUES (?, ?, ?, ?)", 
               (entreprise, email, phone, notes))
            conn.commit()
            conn.close()
            self._show_home_page()
        else:
            warning = customtkinter.CTkLabel(self, text="Le nom de l'entreprise est obligatoire", text_color="red")
            warning.pack(pady=5)
    
    def _clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _defocus_search_entry_on_click(self, event=None):
        event.widget.focus_set() 

    def _defocus_search_entry(self, event=None):
        # Déplacer le focus sur la fenêtre principale ou un autre widget
        event.widget.focus_set() 
    def _show_user_menu(self):
        menu = tkinter.Menu(self, tearoff=0)
        menu.add_command(label="Compte", command=self._account_action)
        menu.add_command(label="Préférences", command=self._preferences_action)
        menu.add_separator()
        menu.add_command(label="Déconnexion", command=self._logout)

        # Position du menu (sous le bouton)
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        menu.tk_popup(x, y)
    def _account_action(self):
        self._clear_window()

        # Conteneur principal
        main_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Colonne gauche
        left_frame = customtkinter.CTkFrame(main_frame, width=200)
        left_frame.pack(side="left", fill="y", padx=(0, 20))

        # Image utilisateur
        user_image = customtkinter.CTkImage(light_image=Image.open("./assets/user.png"), size=(80, 80))
        image_label = customtkinter.CTkLabel(left_frame, image=user_image, text="")
        image_label.pack(pady=(20, 5))

        # Nom utilisateur
        name_label = customtkinter.CTkLabel(left_frame, text=self.current_username, font=("Century Gothic", 14, "bold"))
        name_label.pack(pady=(0, 20))

        # Boutons de menu
        info_button = customtkinter.CTkButton(left_frame, text="Informations", command=self._show_account_info)
        info_button.pack(pady=5, fill="x", padx=10)

        password_button = customtkinter.CTkButton(left_frame, text="Mot de passe", command=self._show_account_password)
        password_button.pack(pady=5, fill="x", padx=10)

        # Séparateur vertical
        separator = customtkinter.CTkFrame(main_frame, width=1, fg_color="#CCCCCC")
        separator.pack(side="left", fill="y")

        # Contenu de droite
        self.right_content_frame = customtkinter.CTkFrame(main_frame)
        self.right_content_frame.pack(side="left", fill="both", expand=True, padx=(20, 0))

        # Affichage par défaut
        self._show_account_info()

    def _show_account_info(self):
        for widget in self.right_content_frame.winfo_children():
            widget.destroy()

        label = customtkinter.CTkLabel(self.right_content_frame, text="Informations du compte", font=("Century Gothic", 16))
        label.pack(pady=20)

        # Ajoute ici les champs info comme email, etc.
    def _show_account_password(self):
        for widget in self.right_content_frame.winfo_children():
            widget.destroy()

        # Titre pour changer le nom d'utilisateur
        label = customtkinter.CTkLabel(self.right_content_frame, text="Changer le nom d'utilisateur", font=("Century Gothic", 16))
        label.pack(pady=(20, 10), anchor="center")

        username_frame = customtkinter.CTkFrame(self.right_content_frame, fg_color="#262624", corner_radius=10)
        username_frame.pack(padx=20, pady=(0, 20), fill="x")

        current_username_label = customtkinter.CTkLabel(username_frame, text="Nom d'utilisateur actuel", font=("Century Gothic", 13))
        current_username_label.pack(pady=(10, 5))

        self.current_username_entry = customtkinter.CTkEntry(username_frame, width=250)
        self.current_username_entry.pack(pady=5)

        self.new_username_label = customtkinter.CTkLabel(username_frame, text="Nouveau nom d'utilisateur", font=("Century Gothic", 13))
        self.new_username_label.pack(pady=(10, 5))

        self.new_username_entry = customtkinter.CTkEntry(username_frame, width=250)
        self.new_username_entry.pack(pady=5)

        self.confirm_username_btn = customtkinter.CTkButton(username_frame, text="Confirmer", command=self._change_username)
        self.confirm_username_btn.pack(pady=20)

        ligne = customtkinter.CTkFrame(self.right_content_frame, height=1, fg_color="#444", corner_radius=0)
        ligne.pack(fill="x", padx=20, pady=(20, 20))

        password_label = customtkinter.CTkLabel(self.right_content_frame, text="Changer le mot de passe", font=("Century Gothic", 16))
        password_label.pack(pady=20)

        password_frame = customtkinter.CTkFrame(self.right_content_frame, fg_color="#262624", corner_radius=10)
        password_frame.pack(padx=20, pady=(0, 20), fill="x")

        # Stocker les champs retournés
        self.current_password_entry = self._create_password_field("Mot de passe actuel", password_frame)
        self.new_password_entry = self._create_password_field("Nouveau mot de passe", password_frame)
        self.confirm_password_entry = self._create_password_field("Confirmer le mot de passe", password_frame)

        btn = customtkinter.CTkButton(password_frame, text="Changer", command=self._change_password)
        btn.pack(pady=20)

    def _create_password_field(self, label_text, parent):
        frame = customtkinter.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=10, padx=20)

        label = customtkinter.CTkLabel(frame, text=label_text, font=("Century Gothic", 13))
        label.pack(pady=(10, 5))

        entry_frame = customtkinter.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack()

        entry = customtkinter.CTkEntry(entry_frame, show="*", width=220)
        entry.pack(side="left", padx=(0, 5))

        def toggle():
            entry.configure(show="" if entry.cget("show") == "*" else "*")

        oeil_btn = customtkinter.CTkButton(entry_frame, text="👁", width=30, command=toggle, fg_color="gray", hover_color="darkgray")
        oeil_btn.pack(side="left")

        return entry  # On retourne l’entrée pour l’utiliser ailleurs


    def _change_username(self):
        old_username = self.current_username_entry.get().strip()
        new_username = self.new_username_entry.get().strip()

        if not old_username or not new_username:
            print("[ERREUR] Les champs ne doivent pas être vides.")
            return

        if old_username != self.current_username:
            print(f"[INFO] Le nom ne correspond pas au nom actuel : '{old_username}' ≠ '{self.current_username}'")
            return

        if old_username == new_username:
            print("[INFO] Le nouveau nom ne peut pas être identique à l'ancien.")
            return

        # Connexion à la base de données
        try:
            conn = sqlite3.connect("./data/users.db")  # Remplace par le nom de ta base
            cursor = conn.cursor()

            # Requête SQL pour mettre à jour
            cursor.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, old_username))
            conn.commit()

            if cursor.rowcount == 0:
                print("[ERREUR] Aucun utilisateur mis à jour. Nom d'utilisateur introuvable.")
            else:
                print(f"[SUCCÈS] Nom d'utilisateur changé : '{old_username}' ➜ '{new_username}'")
                self.current_username = new_username
                self._account_action()  # Mise à jour de l'affichage
                self._show_account_password()

        except sqlite3.Error as e:
            print(f"[ERREUR SQL] {e}")

        finally:
            conn.close()


    def _change_password(self):
        current_password = self.current_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not current_password or not new_password or not confirm_password:
            print("[ERREUR] Tous les champs sont obligatoires.")
            return

        # Vérifier que le mot de passe actuel est correct (requête vers la BDD)
        try:
            conn = sqlite3.connect("./data/users.db")  # Remplace par le chemin de ta base
            cursor = conn.cursor()

            # Récupère le mot de passe actuel en base (à adapter si hashé)
            cursor.execute("SELECT password FROM users WHERE username = ?", (self.current_username,))
            result = cursor.fetchone()

            if not result or result[0] != current_password:
                print("[ERREUR] Mot de passe actuel incorrect.")
                return

            if new_password != confirm_password:
                print("[ERREUR] La confirmation ne correspond pas au nouveau mot de passe.")
                return

            if current_password == new_password:
                print("[INFO] Le nouveau mot de passe doit être différent de l’ancien.")
                return

            # Met à jour le mot de passe
            cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, self.current_username))
            conn.commit()

            if cursor.rowcount == 0:
                print("[ERREUR] Échec de la mise à jour.")
            else:
                print("[SUCCÈS] Mot de passe mis à jour avec succès.")

        except sqlite3.Error as e:
            print(f"[ERREUR SQL] {e}")

        finally:
            conn.close()

    def _show_edit_client_form(self, entreprise, email, phone, notes):
        self._clear_window()

        title = customtkinter.CTkLabel(self, text="Modifier le client", font=("Century Gothic", 24, "bold"))
        title.pack(pady=30)

        self.edit_entry_entreprise = customtkinter.CTkEntry(self, placeholder_text="Nom de l'entreprise", width=400)
        self.edit_entry_entreprise.insert(0, entreprise)
        self.edit_entry_entreprise.pack(pady=10)

        self.edit_entry_email = customtkinter.CTkEntry(self, placeholder_text="Email", width=400)
        self.edit_entry_email.insert(0, email)
        self.edit_entry_email.pack(pady=10)

        self.edit_entry_phone = customtkinter.CTkEntry(self, placeholder_text="Numéro de téléphone", width=400)
        self.edit_entry_phone.insert(0, phone)
        self.edit_entry_phone.pack(pady=10)

        self.edit_entry_notes = customtkinter.CTkEntry(self, placeholder_text="Notes", width=400)
        self.edit_entry_notes.insert(0, notes)
        self.edit_entry_notes.pack(pady=10)

        save_button = customtkinter.CTkButton(
            self,
            text="Changer",
            fg_color="#13B05F",
            hover_color="#0e8a4d",
            width=200,
            command=lambda: self._update_client(entreprise)
        )
        save_button.pack(pady=20)

        cancel_button = customtkinter.CTkButton(
            self,
            text="Annuler",
            fg_color="gray",
            hover_color="darkgray",
            width=200,
            command=self._show_home_page
        )
        cancel_button.pack()


    def _update_client(self, old_entreprise):
        new_entreprise = self.edit_entry_entreprise.get()
        new_email = self.edit_entry_email.get()
        new_phone = self.edit_entry_phone.get()
        new_notes = self.edit_entry_notes.get()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clients 
            SET entreprise = ?, email = ?, phone = ?, notes = ?
            WHERE entreprise = ?
        """, (new_entreprise, new_email, new_phone, new_notes, old_entreprise))
        conn.commit()
        conn.close()
        self._show_home_page()
    def _delete_client(self, entreprise):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE entreprise = ?", (entreprise,))
        conn.commit()
        conn.close()
        self._show_home_page()


    def _preferences_action(self):
        print("Préférences - à implémenter")

    def _logout(self):
        self._show_login_page()

if __name__ == "__main__":
    initialize_database()
    app = MPlusApp()
    app.mainloop()
