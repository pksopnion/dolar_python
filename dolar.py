import requests
import tkinter as tk
from tkinter import Label, Button, OptionMenu, StringVar
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

grafico_atual = None

def obter_preco_moeda(moeda):
    url = f"https://economia.awesomeapi.com.br/json/last/{moeda}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            preco = dados[moeda.replace('-', '')]["bid"]  # Preço atual de compra
            return float(preco)
        else:
            return "Erro"
    except Exception as e:
        return "Erro"

def obter_cotacao_data(moeda, data):
    url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}/365"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            for item in dados:
                timestamp = int(item["timestamp"])
                data_item = time.strftime("%d/%m/%Y", time.localtime(timestamp))
                if data_item == data:
                    return float(item["bid"])
        return "Não disponível"
    except Exception as e:
        return "Erro"

def obter_historico_moeda(moeda, dias=30):
    url = f"https://economia.awesomeapi.com.br/json/daily/{moeda}/{dias}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            historico = [(item["timestamp"], float(item["bid"])) for item in dados]
            historico.sort(key=lambda x: x[0])  # Ordena por timestamp
            return historico
        else:
            return None
    except Exception as e:
        return None

def atualizar_preco():
    while True:
        moeda = moeda_selecionada.get()
        preco = obter_preco_moeda(moeda)
        if preco != "Erro":
            preco_label.config(text=f"Preço atual ({moeda}): R$ {preco:.2f}")
        else:
            preco_label.config(text="Erro ao obter o preço.")

        # Atualiza o preço do dia 25/12/2024
        cotacao_25_12_2024 = obter_cotacao_data(moeda, "25/12/2024")
        if cotacao_25_12_2024 != "Erro" and cotacao_25_12_2024 != "Não disponível":
            preco_25_label.config(text=f"Preço em 25/12/2024: R$ {cotacao_25_12_2024:.2f}")
        else:
            preco_25_label.config(text="Cotação de 25/12/2024 não disponível.")

        time.sleep(10)  # Atualiza a cada 10 segundos

def mostrar_grafico(historico, titulo):
    global grafico_atual

    # Remove o gráfico anterior, se existir
    if grafico_atual is not None:
        grafico_atual.get_tk_widget().destroy()
        grafico_atual = None

    if historico:
        timestamps, precos = zip(*historico)
        datas = [time.strftime("%d/%m/%Y", time.localtime(int(ts))) for ts in timestamps]

        # Criação do gráfico
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(datas, precos, marker="o", linestyle="-", color="blue", label="Cotação")
        ax.set_title(titulo)
        ax.set_xlabel("Data")
        ax.set_ylabel("Preço (R$)")
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45, fontsize=8)  # Reduz tamanho das datas no eixo X

        # Embutindo o gráfico na interface
        grafico_atual = FigureCanvasTkAgg(fig, master=janela)
        canvas_widget = grafico_atual.get_tk_widget()
        canvas_widget.pack(pady=10)
        grafico_atual.draw()
    else:
        preco_label.config(text="Erro ao carregar histórico.")

def mostrar_historico():
    moeda = moeda_selecionada.get()
    historico = obter_historico_moeda(moeda, 30)
    mostrar_grafico(historico, f"Histórico de {moeda} (Últimos 30 Dias)")

janela = tk.Tk()
janela.title("Cotação de Moedas")
janela.geometry("800x600")

titulo_label = Label(janela, text="Cotação de Moedas em Tempo Real", font=("Arial", 16))
titulo_label.pack(pady=10)

preco_label = Label(janela, text="Carregando...", font=("Arial", 14))
preco_label.pack(pady=10)

preco_25_label = Label(janela, text="Carregando...", font=("Arial", 12))
preco_25_label.pack(pady=10)

moedas_disponiveis = ["USD-BRL", "EUR-BRL", "GBP-BRL", "JPY-BRL", "ARS-BRL"]
moeda_selecionada = StringVar(janela)
moeda_selecionada.set(moedas_disponiveis[0])

moeda_menu = OptionMenu(janela, moeda_selecionada, *moedas_disponiveis)
moeda_menu.pack(pady=10)

grafico_button = Button(janela, text="Mostrar Gráfico de 30 Dias", command=mostrar_historico, font=("Arial", 12))
grafico_button.pack(pady=10)

thread = threading.Thread(target=atualizar_preco, daemon=True)
thread.start()

janela.mainloop()
