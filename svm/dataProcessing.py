import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
# from nltk.stem import RSLPStemmer
from nltk.stem import SnowballStemmer
from sklearn.preprocessing import LabelEncoder
import swifter


nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('rslp')
dados = pd.read_csv('dados_v2.csv')

'''
A escolha de tokenizar as palavras (e não as frases) se deu porque as palavras, separadamente, aparentam trazer muito valor categórico às áreas da ciência 
'''

def preProcessing(x_coluna):
    # Removendo espaços e símbolos
    x_coluna = x_coluna.fillna('').str.replace('; ', ';', regex=False)
    x_coluna = x_coluna.str.replace(' ;', ';', regex=False) 
    x_coluna = x_coluna.str.replace(';', ' ', regex=False)
    x_coluna = x_coluna.str.replace(',', ' ', regex=False)

    # Tokenizando
    x_coluna = x_coluna.apply(word_tokenize)

    # Stopwords e Stemming
    # stemmer = RSLPStemmer()
    
    stemmer = SnowballStemmer("portuguese")
    stop_words = set(stopwords.words('portuguese'))
    
    # x_coluna = x_coluna.apply(
    #     lambda tokens: [stemmer.stem(t.lower()) for t in tokens if t.lower() not in stop_words]
    # )
    # Paralelizando a tokenização
    x_coluna = x_coluna.swifter.progress_bar(desc=f"Processando {x_coluna.name}").apply(
        lambda tokens: [stemmer.stem(t.lower()) for t in tokens if t.lower() not in stop_words]
    )
    
    # Juntando para vetorização
    x_coluna = x_coluna.apply(lambda tokens: " ".join(tokens))

    # Retornando coluna preprocessada
    return x_coluna

# tokenizando colunas de entrada
X_titulo = preProcessing(dados['titulo'])
X_resumo = preProcessing(dados['resumo'])
X_palavras = preProcessing(dados['palavrasChave'])

X_concatenado = X_titulo + ' '  + ' ' + X_resumo + ' ' + X_palavras 


dados_processados = pd.DataFrame({
    'titulo_processado': X_titulo,
    'resumo_processado': X_resumo,
    'palavrasChave_processado': X_palavras,
    'texto_concatenado': X_concatenado,
    'classes_originais': dados['areasCiencia']
})

# Salvando em CSV
dados_processados.to_csv('dados_processados.csv', index=False)
