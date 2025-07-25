from ollama import Client
import pandas as pd
from concurrent.futures import ThreadPoolExecutor   # Para fazer chamadas assíncronas/paralelas



examples = """
Classifique o seguinte texto EXCLUSIVAMENTE como uma das seguintes áreas, apenas com a letra: f (Física), q (Química), b (Biologia), c (Ciências-Gerais).
A resposta deve conter apenas a letra da classificação. Exemplos de textos classificados:

Texto: a atitude cibernética aplicada ao ensino de biologia. ensino de biologia; método; modelos;
Classificação: b

Texto: a organização do ensino de física no ciclo básico da universidade. ensino de física; ciclo básico;
Clsasificação: f

Texto: as ciências naturais no currículo da escola normal do paraná. ciências naturais; currículo; escola normal do panamá;
Classificação: c

Texto: a indução como processo de ensino de química. método indutivo; experimento; química.
Classificação: q

"""


df = pd.read_csv('assets/dados_v2.csv')

# Nivela quantidade de amostras entre as áreas de ciência
floor = 300
selected_df = pd.concat([
    df[df['areasCiencia'] == 'f'].sample(floor, random_state=42),
    df[df['areasCiencia'] == 'b'].sample(floor, random_state=42),
    df[df['areasCiencia'] == 'q'].sample(floor, random_state=42),
    df[df['areasCiencia'] == 'c'].sample(floor, random_state=42)
], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

# Cria uma coluna com o texto completo
selected_df['texto_completo'] = selected_df['titulo'] + ' ' + selected_df['areasCiencia']

# Inicializa o cliente do Ollama
client = Client()
response = client.generate(
    model='llama3:8b-instruct-q4_K_M',
    prompt='',
)

selected_df['llama_response'] = ''
areasCiencia = selected_df['areasCiencia'].unique()

for idx, row in selected_df.iterrows():
    
    # Criando prompt completo
    text = row['texto_completo']
    full_prompt = f"{examples}\nTexto: {text}\nClassificação:"
    
    # Faz a chamada ao modelo
    resp = client.generate(
        model='llama3:8b-instruct-q4_K_M',
        prompt=full_prompt,
    )
    
    # Limpa a resposta
    resp_value = resp['response'].strip().lower()
    
    # Verifica resposta fora de padrão
    while resp_value not in areasCiencia:
        print(f"Resposta inválida: {resp_value}. Reenviando...")
        resp = client.generate(
            model='llama3:8b-instruct-q4_K_M',
            prompt=full_prompt,
        )
        resp_value = resp['response'].strip().lower()
        
    selected_df.at[idx, 'llama_response'] = resp_value
    
    # Imprime a resposta
    print(f"({idx+1}/{selected_df.shape[0]}) {row['titulo'][:35]}: {resp['response']}")
    selected_df.at[idx, 'llama_response'] = resp['response']
    if (idx + 1) % 20 == 0:
        print()
        print(f'------------------- acurácia parcial: {((selected_df["llama_response"] == selected_df["areasCiencia"]).sum() / (idx + 1)):.2%} -------------------')
        print()
        selected_df.to_csv('assets/llama_respostas.csv', index=False)

selected_df.to_csv('assets/llama_respostas.csv', index=False)

# Calcula acurácia
accuracy = (selected_df['llama_response'] == selected_df['areasCiencia']).mean()
print(f"Acurácia do modelo: {accuracy:.2%}")