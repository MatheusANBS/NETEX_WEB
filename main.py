import ttkbootstrap as tb
import threading
import requests
import os
import sys
import subprocess
import time
import hashlib

#pyinstaller --onefile --noconsole --icon=netex.ico --clean --name "NETEX"  main.py

VERSAO_ATUAL = "1.0.6"
URL_VERSAO = "https://www.dropbox.com/scl/fi/4x5px3i42f4oabus4xsz1/versao.txt?rlkey=2al2dbgeh1cbs8eb2b7zo5jhk&st=rr21g9fm&dl=1"
URL_EXE = "https://www.dropbox.com/scl/fi/37dcxehu3kjqcjwbpo5ji/NETEX.exe?rlkey=hxlsddbqpi0itu5vfnk4yb6e2&st=kn1t73ct&dl=1"
URL_HASH = "https://www.dropbox.com/scl/fi/773zwxpv2alrdbv6lbsof/hash.txt?rlkey=i0pumc5eqbolxo7n2ybg9jk7n&st=ezjw3v6u&dl=1"

#CertUtil -hashfile NETEX.exe SHA256

def show_update_window(root):
    win = tb.Toplevel(root)
    win.title("Atualização do NETEX")
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.grab_set()
    largura = 400
    altura = 160
    # Centralizar na tela
    win.update_idletasks()
    largura_tela = win.winfo_screenwidth()
    altura_tela = win.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)
    win.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    tb.Label(win, text="Atualização do NETEX", font=("Segoe UI", 14, "bold"), bootstyle="primary").pack(pady=(15, 5))
    status_var = tb.StringVar(value="Verificando atualizações...")
    tb.Label(win, textvariable=status_var, font=("Segoe UI", 11)).pack(pady=(5, 10))
    progress = tb.Progressbar(win, mode="determinate", length=320, bootstyle="info-striped")
    progress.pack(pady=(5, 10))
    progress["value"] = 0
    win.update()
    return win, status_var, progress

def calcular_hash(arquivo, algoritmo="sha256"):
    h = hashlib.new(algoritmo)
    with open(arquivo, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def baixar_update_gui(status_var, progress, win):
    try:
        status_var.set("Verificando atualizações...")
        win.update()
        versao_remota = requests.get(URL_VERSAO, timeout=5).text.strip()
        if versao_remota != VERSAO_ATUAL:
            status_var.set("Atualização disponível! Baixando nova versão...")
            win.update()
            r = requests.get(URL_EXE, stream=True)
            novo_exe = "NETEX_update.exe"
            total = int(r.headers.get('content-length', 0))
            baixado = 0
            chunk_size = 8192
            progress.config(maximum=(total if total > 0 else 100))
            with open(novo_exe, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        baixado += len(chunk)
                        if total > 0:
                            progress.config(value=baixado)
                        else:
                            progress.step(1)
                        win.update()
            # Baixar hash
            status_var.set("Verificando integridade do arquivo...")
            win.update()
            hash_remoto = requests.get(URL_HASH, timeout=5).text.strip()
            hash_local = calcular_hash(novo_exe)
            if hash_local != hash_remoto:
                status_var.set("Falha na verificação de integridade! Atualização abortada.")
                win.update()
                os.remove(novo_exe)
                time.sleep(2)
                win.destroy()
                return
            status_var.set("Atualização concluída! Reiniciando o NETEX...")
            win.update()
            time.sleep(1)
            win.destroy()
            subprocess.Popen([novo_exe])
            sys.exit(0)
        else:
            status_var.set("Nenhuma atualização disponível.")
            win.update()
            time.sleep(1)
            win.destroy()
    except Exception as e:
        status_var.set(f"Erro: {e}")
        win.update()
        time.sleep(2)
        win.destroy()

def checar_atualizacao(root):
    win, status_var, progress = show_update_window(root)
   
    baixar_update_gui(status_var, progress, win)
  

def pos_update():
    exe_name = os.path.basename(sys.argv[0])
    if exe_name.lower() == "netex_update.exe":
        try:
            if os.path.exists("NETEX.exe"):
                os.remove("NETEX.exe")
            os.rename("NETEX_update.exe", "NETEX.exe")
            # Reinicia automaticamente sem pedir confirmação
            subprocess.Popen(["NETEX.exe"])
            time.sleep(1)
            sys.exit(0)
        except Exception as e:
            import ttkbootstrap.dialogs
            ttkbootstrap.dialogs.Messagebox.show_error(f"Erro ao finalizar atualização: {e}", title="Atualização do NETEX")
        sys.exit(0)

def mostrar_confirmacao_reinicio(acao_reiniciar):
    win = tb.Toplevel()
    win.overrideredirect(True)  # Remove bordas e barra de título
    win.attributes("-topmost", True)
    largura, altura = 320, 120
    win.update_idletasks()
    largura_tela = win.winfo_screenwidth()
    altura_tela = win.winfo_screenheight()
    pos_x = (largura_tela // 2) - (largura // 2)
    pos_y = (altura_tela // 2) - (altura // 2)
    win.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
    frame = tb.Frame(win)
    frame.pack(expand=True, fill="both")
    tb.Label(frame, text="Atualização finalizada!\nDeseja reiniciar o NETEX agora?", font=("Segoe UI", 11)).pack(pady=(20, 10))
    tb.Button(frame, text="Reiniciar", bootstyle="success", width=18, command=lambda: [win.destroy(), acao_reiniciar()]).pack(pady=(5, 20))
    win.grab_set()

def main():
    pos_update()
    root = tb.Window(themename="superhero")
    root.withdraw()  
    checar_atualizacao(root)
    root.deiconify()  
    from Modulação.gui import iniciar_interface
    iniciar_interface(root)
    root.mainloop()

if __name__ == "__main__":
    main()