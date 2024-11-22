import os
import time
import string
import nltk
from bs4 import BeautifulSoup
from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from langdetect import detect


def limpar_dados(caminho_arquivo, caminho_destino):
    try:
        # Abrir e ler o arquivo HTML
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        
        # Extrair o título
        titulo = soup.find('h1', class_='textStyle-primary')
        titulo_texto = titulo.get_text(strip=True) if titulo else ""
        
        # Extrair o nome do artista
        artista = soup.find('h2', class_='textStyle-secondary')
        artista_texto = artista.get_text(strip=True) if artista else ""
        
        # Extrair as letras
        div_letras = soup.find('div', class_='lyric-original')
        letras = div_letras.find_all('p') if div_letras else []

        letras_texto = []
        for p in letras:
            # Substituir <br> por espaço dentro do parágrafo
            for br in p.find_all('<br/>'):
                br.replace_with(' ')
            # Adicionar o texto do parágrafo processado à lista
            letras_texto.append(p.get_text(strip=True))

        # Adicionar uma linha em branco entre os parágrafos
        letras_texto = '\n\n'.join(letras_texto)
        #letras_texto = '\n'.join([p.get_text(strip=True) for p in letras])
        
        # Criar o conteúdo do arquivo processado
        conteudo_processado = f"Titulo: {titulo_texto}\n\nArtista: {artista_texto} \n\nLetra:\n{letras_texto}"
        
        # Salvar o conteúdo no diretório de destino
        with open(caminho_destino, 'w', encoding='utf-8') as file:
            file.write(conteudo_processado)
        
        #print(f"Processado: {caminho_arquivo} -> {caminho_destino}")
    except Exception as e:
        print(f"Erro ao processar {caminho_arquivo}: {e}")

# Função para detectar o idioma
def detectar_idioma(texto):
    try:
        return detect(texto)
    except:
        return "unknown"  # Se falhar na detecção, retorna "unknown"

# Função de Análise Léxica: Tokenização
def analise_lexica(texto):
    # Tokeniza o texto em palavras
    tokens = word_tokenize(texto)
    # Remove pontuação e converte as palavras para minúsculas
    tokens = [token.lower() for token in tokens if token not in string.punctuation]
    return tokens

# Função de Remoção de Stopwords
def remover_stopwords(tokens, idioma):
    try:
        stop_words = set(stopwords.words(idioma))  # Usa o idioma detectado
    except:
        stop_words = set()  # Se não houver stopwords para o idioma, não remove nenhuma
    return [token for token in tokens if token not in stop_words]

# Função de Stemming
def stemming(tokens, cod_idioma):
    
    # Mapeamento de códigos ISO 639-1 para nomes usados pelo SnowballStemmer
    ISO_TO_SNOWBALL = {
        "en": "english",
        "pt": "portuguese",
        "es": "spanish",
        "fr": "french",
        "de": "german",
        "it": "italian",
        # Adicione outros idiomas suportados conforme necessário
    }
    idioma = ISO_TO_SNOWBALL.get(cod_idioma)
    
    # Inicializa o SnowballStemmer com base no idioma
    stemmer = SnowballStemmer(idioma) if idioma in SnowballStemmer.languages else None  # Verifica se o idioma é suportado
    return [stemmer.stem(token) if stemmer else token for token in tokens]


# Função de Pré-processamento Completo
def pre_processar(texto):
    idioma = detectar_idioma(texto)  # Detecta o idioma do texto
    #print(f"Idioma detectado: {idioma}")
    
    # Etapa 1: Análise Léxica (tokenização)
    tokens = analise_lexica(texto)
    
    # Etapa 2: Remoção de Stopwords
    tokens_sem_stopwords = remover_stopwords(tokens, idioma)
    
    # Etapa 3: Stemming
    tokens_final = stemming(tokens_sem_stopwords, idioma)
    
    return " ".join(tokens_final)  # Retorna o texto processado

def transformacoes(diretorio_limpo):
    
    arquivos = listar_arquivos_em_diretorio(diretorio_limpo)
    
    # Configura o vetorizador TF-IDF para aprendizado incremental
    vectorizer = TfidfVectorizer(max_features=5000)
    tfidf_matrix = None  # Inicializa a matriz do índice
    
    inicio = time.time()
    for idx, arquivo in enumerate(arquivos):
        
        with open(arquivo, 'r', encoding='utf-8') as file:
            pagina = file.read()
        
        # Atualiza o índice TF-IDF
        texto_vetor = vectorizer.fit_transform([pagina])

        if tfidf_matrix is None:
            tfidf_matrix = vectorizer.fit_transform([pagina])  # Primeiro arquivo
        else:
            texto_vetor = vectorizer.transform([pagina])  # Apenas transforma os dados
            tfidf_matrix = vstack([tfidf_matrix, texto_vetor])  # Adiciona incrementalmente
        
        # Exibe progresso
        if (idx + 1) % 100 == 0 or (idx + 1) == len(arquivos):
            print(f"Processados {idx + 1}/{len(arquivos)} arquivos.")
        
    fim = time.time()
    print(f"Indexação concluída em {fim - inicio:.2f} segundos.")
    
    return tfidf_matrix, vectorizer

def listar_arquivos_em_diretorio(diretorio):
    return [os.path.join(diretorio, arquivo) for arquivo in os.listdir(diretorio) if arquivo.endswith('.html')]

def buscar_por_trecho(trecho, tfidf_matrix, vectorizer):
    # Representa o trecho usando o modelo TF-IDF
    query_vec = vectorizer.transform([trecho])
    
    # Calcula similaridades de cosseno
    similaridades = cosine_similarity(query_vec, tfidf_matrix)
    
    # Ordena resultados por relevância
    resultados = similaridades.argsort()[0][::-1]  # Índices dos textos mais relevantes
    
    return resultados, similaridades


# Diretórios de origem e destino
diretorio_origem = os.path.join(os.getcwd(), 'paginas/A')
diretorio_limpo = os.path.join(os.getcwd(), 'paginas_processadas_teste/A')
diretorio_transformado = os.path.join(os.getcwd(), 'paginas_processadas_teste/A_transformado/')

nltk.download('punkt_tab')
nltk.download('stopwords')

# Criar o diretório de destino, se não existir
os.makedirs(diretorio_limpo, exist_ok=True)


# LIMPAR DADOS

# Iterar pelos arquivos no diretório de origem
# for nome_arquivo in os.listdir(diretorio_origem):
#     caminho_arquivo = os.path.join(diretorio_origem, nome_arquivo)
#     caminho_destino = os.path.join(diretorio_limpos, nome_arquivo)
    
#     if os.path.isfile(caminho_arquivo):  # Certificar que é um arquivo
#         limpar_dados(caminho_arquivo, caminho_destino)


# TRANSFORMAR DADOS

# arquivos = listar_arquivos_em_diretorio(diretorio_limpo)

# for arquivo in arquivos:
#     with open(arquivo, 'r', encoding='utf-8') as file:
#         pagina = file.read()
    
#     #print(pagina[:500])  # Exibe os primeiros 500 caracteres do texto processado
#     texto_processado = pre_processar(pagina)
#     #print(texto_processado[:500])  # Exibe os primeiros 500 caracteres do texto processado
#     dir = os.path.join(diretorio_transformado, os.path.basename(arquivo))
#     with open(dir , 'w', encoding='utf-8') as file:
#         file.write(texto_processado)


# Consulta por trecho
#trecho = "amor liberdade"
#resultados, similaridades = buscar_por_trecho(trecho, tfidf_matrix, vectorizer)

# Exibe os resultados
# print("Resultados:")
# for idx in resultados[:3]:  # Mostra os 3 mais relevantes
#     print(f"Arquivo {idx + 1}: (Similaridade: {similaridades[0][idx]:.2f})")

