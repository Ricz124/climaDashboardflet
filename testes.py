import requests
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
import re

tags = requests.get('https://www.climatempo.com.br/previsao-do-tempo/15-dias/cidade/558/saopaulo-sp')
tag = ''

minMax_list = []
mmChuva_list = []
ventania_list = []
porcentagem_chuva_list = []

for i in tags.text:
    if i != '\n':
        tag += i
    else:
        if 'class="-gray"' in tag:
            tag = tag.split('"')
            minMax = str(tag[2]).replace('>', '').replace('</span', '').replace(' title=', '').replace(' title</p', '').replace('°', '').strip()
            if minMax: 
                minMax_list.append(minMax)
        
        if 'class="_margin-l-5"' in tag:
            tag = tag.split('"')
            mmChuva = str(tag[2]).replace('>', '').replace('</span', '').replace(' title=', '').strip()
            if mmChuva:
                mmChuva_list.append(mmChuva)
                porcentagem_chuva = re.search(r'(\d+)%', tag[2])
                if porcentagem_chuva:
                    porcentagem_chuva_list.append(porcentagem_chuva.group(1))
        
        if 'class="arrow _margin-r-10"' in tag:
            tag = tag.split('"')
            ventania = str(tag[4]).replace('>', '').replace('</span', '').replace(' title=', '').strip()
            if ventania: 
                ventania_list.append(ventania)

        tag = ''

temperaturas_minimas = [float(minMax_list[i]) for i in range(0, len(minMax_list), 2)]
temperaturas_maximas = [float(minMax_list[i]) for i in range(1, len(minMax_list), 2)]
dias = np.arange(len(temperaturas_minimas))

plt.figure(figsize=(10, 6))
plt.plot(dias, temperaturas_minimas, label='Temperaturas Mínimas', marker='o')
plt.plot(dias, temperaturas_maximas, label='Temperaturas Máximas', marker='o')

plt.title('Temperaturas Mínimas e Máximas - 15 Dias')
plt.xlabel('Dias')
plt.ylabel('Temperatura (°C)')
plt.xticks(dias)
plt.legend(loc='upper left')
plt.grid()

plt.savefig('temperaturas.png')
plt.close()

def extrair_valor(valor):
    return float(re.search(r"[\d.]+", valor).group(0)) if re.search(r"[\d.]+", valor) else 0.0

previsao_dia = []
for dia in range(len(temperaturas_minimas)):
    previsao_dia.append({
        "dia": dia + 1,
        "temperatura_minima": temperaturas_minimas[dia],
        "temperatura_maxima": temperaturas_maximas[dia],
        "milimetros_chuva": extrair_valor(mmChuva_list[dia]) if dia < len(mmChuva_list) else 0.0,
        "velocidade_vento": extrair_valor(ventania_list[dia]) if dia < len(ventania_list) else 0.0,
        "porcentagem_chuva": porcentagem_chuva_list[dia] if dia < len(porcentagem_chuva_list) else "0"
    })

def main(page: ft.Page):
    page.title = "Previsão do Tempo Detalhada"
    page.scroll = ft.ScrollMode.ALWAYS

    img = ft.Image(src='temperaturas.png', width=800)

    temp_infos = ft.Column(spacing=10)
    for previsao in previsao_dia:
        card = ft.Card(
            content=ft.Column(
                [
                    ft.Text(f"Dia {previsao['dia']}", weight="bold", size=20),
                    ft.Row([
                        ft.Text(f"Temperatura Mínima: {previsao['temperatura_minima']}°C", color=ft.colors.BLUE),
                        ft.Text(f"Temperatura Máxima: {previsao['temperatura_maxima']}°C", color=ft.colors.RED)
                    ]),
                    ft.Row([
                        ft.Text(f"Chuva: {previsao['milimetros_chuva']} mm", color=ft.colors.GREEN),
                        ft.Text(f"Vento: {previsao['velocidade_vento']} km/h", color=ft.colors.ORANGE)
                    ]),
                    ft.Text(f"Chance de Chuva: {previsao['porcentagem_chuva']}%", color=ft.colors.PURPLE)
                ],
                alignment=ft.MainAxisAlignment.START,
                spacing=5
            ),
            elevation=5
        )
        temp_infos.controls.append(card)

    page.add(img, temp_infos)

ft.app(target=main)
