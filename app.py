import streamlit as st
import pandas as pd
import io
import re
import os
import unicodedata

# --- CONFIGURAÇÃO DA PÁGINA DEVE SER O PRIMEIRO COMANDO STREAMLIT ---
st.set_page_config(page_title="Roadtrips Ibéricas", page_icon="🚗", layout="wide")

# 1. Os dados limpos
csv_data = """Origem;Destino;Opção;Tempo;Preço
Alicante;Almeria;1;3 h 07 min;37,9
Alicante;Almeria;2;3 h 27 min;38,4
Alicante;Almeria;3;3 h 15 min;37,4
Alicante;Madrid;1;4 h 21 min;57,6
Alicante;Madrid;2;4 h 30 min;53,9
Alicante;Málaga;1;5 h 04 min;60,7
Alicante;Salamanca;1;6 h 32 min;114,1
Alicante;Salamanca;2;6 h 57 min;81,0
Alicante;Salamanca;3;7 h 20 min;98,9
Alicante;Sevilha;1;6 h 28 min;59,2
Alicante;Toledo;1;4 h 16 min;54,2
Alicante;Toledo;2;4 h 34 min;57,4
Alicante;Valência;1;2 h 13 min;21,4
Alicante;Valência;2;2 h 23 min;20,7
Almeria;Alicante;1;3 h 06 min;37,9
Almeria;Alicante;2;3 h 28 min;38,5
Almeria;Alicante;3;3 h 35 min;37,3
Almeria;Sevilha;1;4 h 40 min;39,6
Almeria;Sevilha;2;4 h 49 min;38,8
Almeria;Sevilha;3;4 h 40 min;40,3
Almeria;Valência;1;4 h 32 min;54,4
Almeria;Valência;2;4 h 58 min;55,2
Almeria;Valência;3;5 h 01 min;53,8
Barcelos;Madrid;1;6 h 15 min;99,4
Barcelos;Madrid;2;7 h 41 min;74,2
Barcelos;Madrid;3;8 h 41 min;93,8
Barcelos;Salamanca;1;4 h 33 min;59,1
Barcelos;Salamanca;2;5 h 28 min;50,3
Barcelos;Salamanca;3;6 h 40 min;56,4
Barcelos;Sevilha;1;7 h 46 min;93,4
Barcelos;Sevilha;2;8 h 39 min;83,1
Barcelos;Sevilha;3;8 h 57 min;98,9
Barcelos;Toledo;1;6 h 54 min;108,3
Barcelos;Toledo;2;7 h 41 min;82,3
Barcelos;Toledo;3;9 h 36 min;86,7
Madrid;Alicante;1;4 h 25 min;53,9
Madrid;Barcelos;1;6 h 24 min;100,3
Madrid;Barcelos;2;7 h 57 min;74,2
Madrid;Barcelos;3;8 h 49 min;94,3
Madrid;Valência;1;3 h 59 min;45,7
Málaga;Alicante;1;5 h 03 min;60,7
Málaga;Sevilha;1;2 h 35 min;20,1
Salamanca;Alicante;1;6 h 30 min;113,9
Salamanca;Alicante;2;7 h 01 min;80,7
Salamanca;Alicante;3;7 h 06 min;99,5
Salamanca;Barcelos;1;4 h 31 min;59,1
Salamanca;Barcelos;2;5 h 22 min;50,2
Salamanca;Barcelos;3;6 h 52 min;55,9
Salamanca;Valência;1;6 h 16 min;87,5
Salamanca;Valência;2;6 h 33 min;72,4
Salamanca;Valência;3;7 h 01 min;73,6
Sevilha;Alicante;1;6 h 24 min;59,2
Sevilha;Almeria;1;4 h 31 min;40,2
Sevilha;Almeria;2;4 h 52 min;39,1
Sevilha;Barcelos;1;7 h 51 min;94,5
Sevilha;Barcelos;2;8 h 43 min;84,9
Sevilha;Barcelos;3;9 h 07 min;97,4
Sevilha;Málaga;1;2 h 32 min;20,1
Sevilha;Valência;1;6 h 57 min;65,8
Sevilha;Valência;2;8 h 26 min;67,6
Sevilha;Valência;3;7 h 27 min;64,6
Toledo;Alicante;1;4 h 16 min;54,2
Toledo;Alicante;2;4 h 30 min;57,5
Toledo;Barcelos;1;6 h 54 min;109,1
Toledo;Barcelos;2;7 h 28 min;84,9
Toledo;Barcelos;3;10 h 12 min;86,2
Toledo;Valência;1;4 h 18 min;47,6
Toledo;Valência;2;4 h 24 min;49,6
Valência;Alicante;1;1 h 59 min;21,0
Valência;Alicante;2;2 h 13 min;20,7
Valência;Almeria;1;4 h 31 min;54,3
Valência;Almeria;2;4 h 51 min;54,9
Valência;Madrid;1;3 h 45 min;49,3
Valência;Madrid;2;3 h 49 min;45,7
Valência;Málaga;1;6 h 28 min;77,1
Valência;Málaga;2;7 h 01 min;73,4
Valência;Salamanca;1;6 h 07 min;87,7
Valência;Salamanca;2;6 h 50 min;73,7
Valência;Salamanca;3;6 h 27 min;86,4
Valência;Sevilha;1;6 h 50 min;65,8
Valência;Sevilha;2;8 h 23 min;68,1
Valência;Toledo;1;3 h 58 min;49,4
Valência;Toledo;2;4 h 06 min;49,6
Valência;Toledo;3;4 h 11 min;46,6"""

# 2. Funções de Suporte
def converter_para_minutos(tempo_str):
    """Lê a string 'X h Y min' e devolve o total em minutos."""
    horas, minutos = 0, 0
    match_h = re.search(r'(\d+)\s*h', str(tempo_str))
    match_m = re.search(r'(\d+)\s*min', str(tempo_str))
    
    if match_h:
        horas = int(match_h.group(1))
    if match_m:
        minutos = int(match_m.group(1))
        
    return (horas * 60) + minutos

def converter_para_texto(minutos_totais):
    """Converte os minutos totais de volta para 'X h Y min'."""
    horas = minutos_totais // 60
    minutos = minutos_totais % 60
    return f"{horas} h {minutos:02d} min"

def normalizar_nome(texto):
    """Remove acentos e converte para minúsculas."""
    texto_sem_acentos = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto_sem_acentos.lower()

# 3. Carregar o DataFrame
@st.cache_data
def carregar_dados():
    df = pd.read_csv(io.StringIO(csv_data), sep=";")
    df['Preço'] = df['Preço'].astype(str).str.replace(',', '.').astype(float)
    return df

df = carregar_dados()

def obter_viagens(origem, destino):
    return df[(df['Origem'] == origem) & (df['Destino'] == destino)]

# --- INTERFACE (UI) ---

st.title("🚗 Planeador de Roadtrips Ibéricas")
st.markdown("Cria o teu itinerário a partir de **Barcelos** para a praia, escolhendo as paragens e a melhor opção de viagem!")

# Grupos de Cidades
grupo_1_4_5 = ["Madrid", "Toledo", "Salamanca", "Málaga", "Almeria", "Sevilha"]
grupo_2_3 = ["Valência", "Alicante"]

# Dropdowns de Seleção de Cidades
col_cidade1, col_cidade2, col_cidade3 = st.columns(3)

with col_cidade1:
    st.info("🏁 **Partida:** Barcelos")
    paragem1 = st.selectbox("📍 1ª Paragem (Ida):", grupo_1_4_5, index=2) # Salamanca por defeito
    parar_sevilha_ida = False
    if paragem1 in ["Almeria", "Málaga"]:
        st.warning(f"A viagem direta para {paragem1} é muito grande!")
        parar_sevilha_ida = st.checkbox(f"Fazer paragem em Sevilha na ida?", value=True)

with col_cidade2:
    destino_principal = st.selectbox("🏖️ Destino (Praia):", grupo_2_3, index=0)
    visitar_ambas = st.checkbox("Visitar Valência E Alicante?", value=False)

with col_cidade3:
    paragem2 = st.selectbox("📍 2ª Paragem (Regresso):", grupo_1_4_5, index=0) # Madrid por defeito
    parar_sevilha_regresso = False
    if paragem2 in ["Almeria", "Málaga"]:
        st.warning(f"A viagem direta a partir de {paragem2} é muito grande!")
        parar_sevilha_regresso = st.checkbox(f"Fazer paragem em Sevilha no regresso?", value=True)
    st.info("🏁 **Chegada:** Barcelos")

st.divider()

# --- CÁLCULO E ESCOLHA DE ITINERÁRIO ---
st.header("🗺️ Escolhe as Opções de Viagem")

# Construção dinâmica da Rota
rotas = []

# 1. Trajeto de Ida (com ou sem Sevilha)
if parar_sevilha_ida:
    rotas.extend([("Barcelos", "Sevilha"), ("Sevilha", paragem1)])
else:
    rotas.append(("Barcelos", paragem1))

# 2. Ida para a Praia
rotas.append((paragem1, destino_principal))

# 3. Trajeto entre Praias (se ativado)
if visitar_ambas:
    segunda_praia = "Alicante" if destino_principal == "Valência" else "Valência"
    rotas.append((destino_principal, segunda_praia))
    praia_saida = segunda_praia
else:
    praia_saida = destino_principal

# 4. Regresso a partir da Praia
rotas.append((praia_saida, paragem2))

# 5. Trajeto Final (com ou sem Sevilha)
if parar_sevilha_regresso:
    rotas.extend([(paragem2, "Sevilha"), ("Sevilha", "Barcelos")])
else:
    rotas.append((paragem2, "Barcelos"))


custo_total = 0.0
tempo_total_minutos = 0
viagem_viavel = True

# Criar colunas baseadas no tamanho dinâmico da rota
cols_viagem = st.columns(len(rotas))

for i, (orig, dest) in enumerate(rotas):
    viagens_disponiveis = obter_viagens(orig, dest)
    
    with cols_viagem[i]:
        st.subheader(f"Etapa {i+1}")
        st.write(f"**{orig}** ➔ \n**{dest}**")
        
        # --- CARREGAR IMAGEM (NORMALIZADA) ---
        orig_norm = normalizar_nome(orig)
        dest_norm = normalizar_nome(dest)
        nome_imagem = f"{orig_norm}_{dest_norm}_viagem.png"
        
        if os.path.exists(nome_imagem):
            st.image(nome_imagem, use_container_width=True)
        else:
            st.caption(f"*(Imagem não encontrada: {nome_imagem})*")
        # ------------------------------------

        if not viagens_disponiveis.empty:
            def formatar_opcao(idx):
                linha = viagens_disponiveis.loc[idx]
                return f"Op. {linha['Opção']} ({linha['Preço']:.2f}€ | {linha['Tempo']})"

            escolha_idx = st.selectbox(
                "Escolhe a opção:", 
                viagens_disponiveis.index, 
                format_func=formatar_opcao, 
                key=f"rota_{orig}_{dest}_{i}"
            )
            
            viagem_escolhida = viagens_disponiveis.loc[escolha_idx]
            preco = viagem_escolhida['Preço']
            tempo_str = viagem_escolhida['Tempo']
            
            custo_total += preco
            tempo_total_minutos += converter_para_minutos(tempo_str)
            
            st.success(f"💶 {preco:.2f} €")
            st.caption(f"⏱️ Tempo: {tempo_str}")
            
        else:
            st.error("Rota não encontrada nos dados!")
            viagem_viavel = False

st.divider()

# --- RESULTADO FINAL ---
if viagem_viavel:
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        st.metric(label="💰 Custo Total (Combustível + Portagens)", value=f"{custo_total:.2f} €")
        
        viajantes = st.slider("👥 Número de Viajantes (para dividir a conta)", min_value=1, max_value=5, value=2)
        if viajantes > 1:
            st.info(f"O custo por pessoa fica a **{(custo_total / viajantes):.2f} €**.")
            
    with col_res2:
        tempo_formatado = converter_para_texto(tempo_total_minutos)
        st.metric(label="⏱️ Tempo Total de Condução", value=tempo_formatado)
        st.caption("Isto é o tempo de condução somado (não inclui as tuas paragens turísticas/dormidas).")
else:
    st.warning("⚠️ O percurso escolhido contém rotas que não constam nos teus dados. Tenta alterar as cidades!")