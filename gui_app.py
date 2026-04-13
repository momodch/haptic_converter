import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from .wav_to_haps import wav_to_haps


def select_wav():
    file_path = filedialog.askopenfilename(
        title="Sélectionner un fichier WAV",
        filetypes=[("Fichiers WAV", "*.wav")]
    )
    if file_path:
        wav_entry.delete(0, tk.END)
        wav_entry.insert(0, file_path)


def select_output():
    file_path = filedialog.asksaveasfilename(
        title="Sauvegarder en tant que fichier HAPS",
        defaultextension=".haps",
        filetypes=[("Fichiers HAPS", "*.haps")]
    )
    if file_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file_path)


def run_conversion():
    wav_path = wav_entry.get()
    output_path = output_entry.get()
    mode = mode_var.get()

    if not wav_path or not output_path:
        messagebox.showerror("Erreur", "Veuillez sélectionner les fichiers.")
        return

    try:
        wav_to_haps(wav_path, output_path, mode=mode)
        messagebox.showinfo("Succès", "Conversion terminée avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# Interface principale
root = tk.Tk()
root.title("WAV → HAPS Converter")
root.geometry("500x250")

# Sélection fichier WAV
tk.Label(root, text="Fichier WAV :").pack(pady=5)
frame_wav = tk.Frame(root)
frame_wav.pack(fill="x", padx=10)
wav_entry = tk.Entry(frame_wav)
wav_entry.pack(side="left", fill="x", expand=True)
tk.Button(frame_wav, text="Parcourir", command=select_wav).pack(side="right", padx=5)

# Sélection fichier HAPS
tk.Label(root, text="Fichier HAPS :").pack(pady=5)
frame_out = tk.Frame(root)
frame_out.pack(fill="x", padx=10)
output_entry = tk.Entry(frame_out)
output_entry.pack(side="left", fill="x", expand=True)
tk.Button(frame_out, text="Parcourir", command=select_output).pack(side="right", padx=5)

# Mode
tk.Label(root, text="Mode de conversion :").pack(pady=5)
mode_var = tk.StringVar(value="Audio to haptic")
mode_menu = ttk.Combobox(root, textvariable=mode_var, values=["Audio to haptic", "Subwoofer for headset"], state="readonly")
mode_menu.pack(pady=5)

# Bouton conversion
tk.Button(root, text="Convertir", command=run_conversion, bg="#4CAF50", fg="white").pack(pady=15)

root.mainloop()
