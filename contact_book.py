import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = "contacts.json"

# Load contacts from JSON
def load_contacts():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Save contacts to JSON
def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=4)

class ContactBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazing Contact Book")
        self.root.geometry("600x500")
        self.contacts = load_contacts()

        self.create_widgets()
        self.display_contacts()

    def create_widgets(self):
        # Frame for search bar
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda name, index, mode: self.display_contacts())
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT)

        # Frame for contact list with scrollbar
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.contact_listbox = tk.Listbox(list_frame, font=("Arial", 12))
        self.contact_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        scrollbar.config(command=self.contact_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.contact_listbox.config(yscrollcommand=scrollbar.set)

        self.contact_listbox.bind("<Double-1>", self.open_contact_details)

        # Frame for numpad and number entry
        numpad_frame = tk.LabelFrame(self.root, text="Numpad Search / Add", padx=5, pady=5)
        numpad_frame.pack(pady=5)

        self.number_entry = tk.Entry(numpad_frame, font=("Arial", 14), width=20)
        self.number_entry.grid(row=0, column=0, columnspan=3, pady=5)

        buttons = [
            ('1',1,0),('2',1,1),('3',1,2),
            ('4',2,0),('5',2,1),('6',2,2),
            ('7',3,0),('8',3,1),('9',3,2),
            ('0',4,1)
        ]
        for (text, r, c) in buttons:
            tk.Button(numpad_frame, text=text, width=5, height=2,
                      command=lambda digit=text: self.number_entry.insert(tk.END, digit)
                      ).grid(row=r, column=c, padx=2, pady=2)

        tk.Button(numpad_frame, text="Search Number", width=16, command=self.search_number
                  ).grid(row=4, column=0, columnspan=1, pady=5)

        tk.Button(numpad_frame, text="Clear", width=16, command=lambda: self.number_entry.delete(0, tk.END)
                  ).grid(row=4, column=2, columnspan=1, pady=5)

        # Button to add new contact manually
        tk.Button(self.root, text="Add New Contact", width=20, command=self.add_new_contact
                  ).pack(pady=5)

    def display_contacts(self):
        search_term = self.search_var.get().lower()
        self.contact_listbox.delete(0, tk.END)
        for name in sorted(self.contacts.keys()):
            if search_term in name.lower():
                self.contact_listbox.insert(tk.END, name)

    def open_contact_details(self, event):
        selection = self.contact_listbox.curselection()
        if not selection:
            return
        name = self.contact_listbox.get(selection[0])
        numbers = "\n".join(self.contacts[name])
        messagebox.showinfo("Contact Details", f"Name: {name}\nNumbers:\n{numbers}")

    def search_number(self):
        number = self.number_entry.get()
        if not number:
            messagebox.showwarning("Input Error", "Please enter a number.")
            return
        found = False
        for name, numbers in self.contacts.items():
            if number in numbers:
                found = True
                if messagebox.askyesno("Number Found", f"This number belongs to {name}. View details?"):
                    self.show_contact_info(name)
                break
        if not found:
            if messagebox.askyesno("Number Not Found", "Number not found.\nDo you want to add it as a new contact?"):
                self.add_new_contact(number)
            else:
                self.add_to_existing_contact(number)

    def show_contact_info(self, name):
        numbers = "\n".join(self.contacts[name])
        messagebox.showinfo("Contact Info", f"Name: {name}\nNumbers:\n{numbers}")

    def add_new_contact(self, prefill_number=None):
        name = simpledialog.askstring("New Contact", "Enter contact name:")
        if not name:
            return
        if name in self.contacts:
            messagebox.showerror("Duplicate Name", "This name already exists. Please use a different name.")
            return
        number = prefill_number or simpledialog.askstring("New Contact", "Enter phone number:")
        if not number:
            return
        self.contacts[name] = [number]
        save_contacts(self.contacts)
        self.display_contacts()
        messagebox.showinfo("Success", "Contact added successfully.")

    def add_to_existing_contact(self, number):
        names = sorted(self.contacts.keys())
        if not names:
            messagebox.showinfo("No Contacts", "No existing contacts to add number to.")
            return
        name = simpledialog.askstring("Add to Contact", f"Enter the name of contact to add number to:\n{', '.join(names)}")
        if not name or name not in self.contacts:
            messagebox.showerror("Invalid Name", "Name not found.")
            return
        if number in self.contacts[name]:
            messagebox.showinfo("Duplicate Number", "This number already exists for this contact.")
            return
        self.contacts[name].append(number)
        save_contacts(self.contacts)
        messagebox.showinfo("Success", "Number added successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()
