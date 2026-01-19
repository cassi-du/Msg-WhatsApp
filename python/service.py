import pandas as pd
import re
import matplotlib.pyplot as plt
from pathlib import Path

def processar_chat(
    caminho_txt: str,
    output_dir: str = "output",
    periodo: str = "W"  # 'D', 'W', 'M'
):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    padrao = r'\[(\d{2}/\d{2}/\d{2}),\s(\d{2}:\d{2}:\d{2}\s(?:AM|PM))\]\s(.+?):\s(.+?)(?=\n\[|$)'

    with open(caminho_txt, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    mensagens = re.findall(padrao, conteudo, re.DOTALL)

    dados = []
    for data, hora, remetente, mensagem in mensagens:
        mensagem = mensagem.strip()

        if 'omitted' in mensagem.lower() or 'encrypted' in mensagem.lower():
            continue

        data_dt = pd.to_datetime(
            f"{data} {hora}",
            format="%d/%m/%y %I:%M:%S %p",
            errors="coerce"
        )

        dados.append({
            'data': data,
            'hora': hora,
            'data_dt': data_dt,
            'remetente': remetente.strip(),
            'mensagem': mensagem
        })

    df = (
        pd.DataFrame(dados)
        .dropna(subset=['data_dt'])
        .sort_values('data_dt')
        .reset_index(drop=True)
    )

    # =======================
    # Tempo de resposta
    # =======================
    df_resp = df.copy()
    df_resp['remetente_anterior'] = df_resp['remetente'].shift(1)
    df_resp['data_anterior'] = df_resp['data_dt'].shift(1)

    df_resp['tempo_resposta_min'] = (
        (df_resp['data_dt'] - df_resp['data_anterior'])
        .dt.total_seconds() / 60
    )

    df_resp = df_resp[
        (df_resp['remetente'] != df_resp['remetente_anterior']) &
        (df_resp['tempo_resposta_min'] > 0) &
        (df_resp['tempo_resposta_min'] < 720)
    ]

    periodo_nome = {'D': 'Dia', 'W': 'Semana', 'M': 'Mês'}[periodo]

    # =======================
    # Gráfico 1 — Mensagens por período
    # =======================
    msgs_periodo = (
        df
        .set_index('data_dt')
        .groupby([pd.Grouper(freq=periodo), 'remetente'])
        .size()
        .unstack(fill_value=0)
    )

    plt.figure(figsize=(14,6))
    msgs_periodo.plot(kind='bar', width=0.8)
    plt.title(f'Mensagens por {periodo_nome} e Remetente')
    plt.xlabel(periodo_nome)
    plt.ylabel('Quantidade')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    graf1 = output / "mensagens_por_periodo.png"
    plt.savefig(graf1)
    plt.close()

    # =======================
    # Gráfico 2 — Pizza
    # =======================
    plt.figure(figsize=(7,7))
    df['remetente'].value_counts().plot.pie(
        autopct='%1.1f%%',
        startangle=90
    )
    plt.title('Distribuição de Mensagens')
    plt.tight_layout()
    graf2 = output / "distribuicao_remetentes.png"
    plt.savefig(graf2)
    plt.close()

    # =======================
    # Gráfico 3 — Tempo médio resposta
    # =======================
    tempo_medio = (
        df_resp
        .set_index('data_dt')
        .groupby([pd.Grouper(freq=periodo), 'remetente'])['tempo_resposta_min']
        .mean()
        .unstack()
    )

    plt.figure(figsize=(14,6))
    tempo_medio.plot(kind='bar', width=0.8)
    plt.title(f'Tempo Médio de Resposta ({periodo_nome})')
    plt.ylabel('Minutos')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    graf3 = output / "tempo_medio_resposta.png"
    plt.savefig(graf3)
    plt.close()

    return {
        "total_mensagens": len(df),
        "remetentes": df['remetente'].unique().tolist(),
        "graficos": [
            str(graf1),
            str(graf2),
            str(graf3)
        ]
    }