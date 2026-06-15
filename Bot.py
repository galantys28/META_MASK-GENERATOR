import random
import requests
from eth_account import Account
import tkinter as tk
from tkinter import filedialog, messagebox

# Увімкнути HD-гаманці (mnemonic/BIP44) в eth_account
Account.enable_unaudited_hdwallet_features()

API_URL = "https://randomuser.me/api/?results={}&nat=us,gb,ca,au,nz"


def generate_names(count):
    names = []
    try:
        response = requests.get(API_URL.format(count))
        data = response.json()
        for user in data['results']:
            first = user['name']['first']
            last = user['name']['last']
            name = f"{first} {last}"
            # тільки ASCII, щоб не було кривих символів
            if all(ord(c) < 128 for c in name):
                names.append(name)
            else:
                names.append(
                    f"Name{random.randint(1000, 9999)}Surname{random.randint(1000, 9999)}"
                )
    except Exception:
        # запасний варіант, якщо API впаде
        for i in range(count):
            names.append(f"Name{i+1}Surname{i+1}")
    return names


def generate_wallet():
    """
    Генеруємо:
    - новий акаунт (LocalAccount)
    - сід-фразу (mnemonic) для нього

    eth_account гарантує, що:
    acct == Account.from_mnemonic(mnemonic)
    при однаковому account_path (дефолт: m/44'/60'/0'/0/0)
    """
    acct, mnemonic = Account.create_with_mnemonic(
        num_words=12,           # 12 слів, як у MetaMask
        # account_path="m/44'/60'/0'/0/0"  # можна не вказувати, це дефолт
    )
    address = acct.address
    private_key = acct.key.hex()
    seed_phrase = mnemonic
    return address, private_key, seed_phrase


def save_wallets(count, include_name, include_private_key, filename):
    names = generate_names(count) if include_name else ["" for _ in range(count)]
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(count):
            name = names[i]
            address, private_key, seed_phrase = generate_wallet()

            parts = []

            # Ім'я (якщо вибрано)
            if include_name:
                parts.append(name)

            # Адреса гаманця
            parts.append(address)

            # Приватний ключ (якщо вибрано)
            if include_private_key:
                parts.append(private_key)

            # Сід-фраза — завжди остання
            parts.append(seed_phrase)

            # Без пробілів навколо '|'
            line = "|".join(parts)
            f.write(line + "\n")


def generate():
    try:
        val = entry_count.get().strip()
        if not val.isdigit():
            raise ValueError
        count = int(val)
        include_name = var_name.get()
        include_key = var_key.get()
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            save_wallets(count, include_name, include_key, filename)
            messagebox.showinfo("Успіх", f"Згенеровано {count} гаманців у файл:\n{filename}")
    except ValueError:
        messagebox.showerror("Помилка", "Введіть правильну кількість гаманців.")


# GUI
root = tk.Tk()
root.title("MetaMask Wallet Generator")
root.geometry("400x250")

tk.Label(root, text="Кількість гаманців:").pack(pady=5)
entry_count = tk.Entry(root)
entry_count.pack(pady=5)

var_name = tk.BooleanVar()
var_key = tk.BooleanVar()

tk.Checkbutton(root, text="Додавати ім'я та прізвище", variable=var_name).pack()
tk.Checkbutton(root, text="Додавати приватний ключ", variable=var_key).pack()

tk.Button(root, text="Згенерувати та зберегти в .txt", command=generate).pack(pady=20)

root.mainloop()
