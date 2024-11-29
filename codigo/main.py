import os
import time
import sys
import string
import nltk
import psutil
import joblib
from bs4 import BeautifulSoup
from scipy.sparse import vstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
from langdetect import detect

# MAIN ATUALIZADA

# Função para limpar dados html e deixar apenas o texto de interesse (titulo, artista e letra)
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
            # Substituir todas as tags <br> por um espaço dentro do parágrafo
            for br in p.find_all('br'):
                br.replace_with(' ')  # Substitui <br> por espaço
            
            # Adicionar o texto do parágrafo processado à lista
            letras_texto.append(p.get_text(strip=False))
        
        # Adicionar uma linha em branco entre os parágrafos
        letras_texto = '\n\n'.join(letras_texto)
        #letras_texto = '\n'.join([p.get_text(strip=True) for p in letras])
        
        # Criar o conteúdo do arquivo processado
        conteudo_processado = f"Titulo:\n{titulo_texto}\n\nArtista:\n{artista_texto} \n\nLetra:\n{letras_texto}"
        caminho_destino = caminho_destino[:-4] + 'txt'
        # Salvar o conteúdo no diretório de destino
        with open(caminho_destino, 'w', encoding='utf-8') as file:
            file.write(conteudo_processado)
        
        #print(f"Processado: {caminho_arquivo} -> {caminho_destino}")
    except Exception as e:
        print(f"Erro ao processar {caminho_arquivo}: {e}")

def filtrar_limpar_dados(diretorio_origem, diretorio_limpo ):
    for nome_arquivo in os.listdir(diretorio_origem):
        caminho_arquivo = os.path.join(diretorio_origem, nome_arquivo)
        caminho_destino = os.path.join(diretorio_limpo, nome_arquivo)

        if os.path.isfile(caminho_arquivo):  # Certificar que é um arquivo
            limpar_dados(caminho_arquivo, caminho_destino)

# Função para detectar o idioma
def detectar_idioma(texto):
    try:
        return detect(texto)
    except:
        return "unknown"  # Se falhar na detecção, retorna "unknown"

def idioma_para_nome(iso_code):
    idiomas = {
        "en": "english",
        "es": "spanish",
        "fr": "french",
        "de": "german",
        "pt": "portuguese",
        "it": "italian",
        "ru": "russian",
        "ja": "japanese",
        "zh": "chinese",
        "ko": "korean"
    }
    return idiomas.get(iso_code, "Idioma desconhecido")

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
        stop_words = set(stopwords.words(idioma_para_nome(idioma)))  # Usa o idioma detectado
    except:
        stop_words = set()  # Se não houver stopwords para o idioma, não remove nenhuma
    return [token for token in tokens if token not in stop_words]

# Função de Stemming
def stemming(tokens, idioma):
    
    # Inicializa o SnowballStemmer com base no idioma
    stemmer = SnowballStemmer(idioma_para_nome(idioma)) if idioma in SnowballStemmer.languages else None  # Verifica se o idioma é suportado
    return [stemmer.stem(token) if stemmer else token for token in tokens]

# Função de Pré-processamento Completo
def pre_processar(texto):
    # Detecta o idioma do texto
    idioma = detectar_idioma(texto)

    # Etapa 1: Substituir quebras de linha por um marcador temporário
    texto_com_quebras = texto.replace("\n", "__line__ ")

    # Etapa 2: Análise Léxica (tokenização)
    tokens = analise_lexica(texto_com_quebras)
    
    # Etapa 3: Remoção de Stopwords
    #tokens_sem_stopwords = remover_stopwords(tokens, idioma)
    
    # Etapa 4: Stemming
    tokens_final = stemming(tokens, idioma) # PARA UTILIZAR REOMÇÃO DE STOPWORDS DEVE TROCAR O PARAMETRO TOKENS PARA TOKENS_SEM_STOPWORDS
    
    # Etapa 5: Restaurar as quebras de linha
    texto_processado = " ".join(tokens_final).replace("__line__ ", "\n")

    return texto_processado  # Retorna o texto processado

# Função para listar os arquivos do diretório
def listar_arquivos_em_diretorio(diretorio):
    return [os.path.join(diretorio, arquivo) for arquivo in os.listdir(diretorio)]

# Função para realizar indexação de TF-IDF
def tf_idf(diretorio, batch_size):
    arquivos = listar_arquivos_em_diretorio(diretorio)  
    vectorizer = TfidfVectorizer(max_features=30000000, ngram_range=(1, 3))  
    tfidf_matrix = None  
    vocabulario_construido = False  
    
    textos = []
    for idx in range(0, len(arquivos), batch_size):
        batch_arquivos = arquivos[idx:idx+batch_size]
        textos = []
        for arquivo in batch_arquivos:
            with open(arquivo, 'r', encoding='utf-8') as file:
                linhas = file.readlines()
                texto_filtrado = ''.join(linhas[:2] + linhas[7:])  # Ignora as linhas 3, 4, 5, 6 e 7
                textos.append(texto_filtrado)

        
        if not vocabulario_construido:
            tfidf_matrix = vectorizer.fit_transform(textos)
            vocabulario_construido = True
        else:
            texto_vetor = vectorizer.transform(textos)
            tfidf_matrix = vstack([tfidf_matrix, texto_vetor])

        print(f"Processados {min(idx + batch_size, len(arquivos))}/{len(arquivos)} arquivos.")

    salvar_indice(tfidf_matrix, vectorizer)
    return tfidf_matrix, vectorizer

# Função para realizar indexação e avaliar tempo e espaço utilizados para processar
def avaliar_tempo_espaco_indexacao(diretorio, batch_size=10000):

    inicio_tempo = time.time()
    memoria_inicial = psutil.Process().memory_info().rss  

    tfidf_matrix, vectorizer = tf_idf(diretorio, batch_size)

    fim_tempo = time.time()
    memoria_final = psutil.Process().memory_info().rss  

    tempo_total = fim_tempo - inicio_tempo
    memoria_usada = (memoria_final - memoria_inicial) / (1024 * 1024)  

    print(f"\nTempo total de indexação: {tempo_total:.2f} segundos")
    print(f"Memória utilizada: {memoria_usada:.2f} MB")

    return tfidf_matrix, vectorizer

def medir_tamanho_do_indice(tfidf_matrix):
    # Tamanho da matriz esparsa em bytes
    return sys.getsizeof(tfidf_matrix.data) + sys.getsizeof(tfidf_matrix.indices) + sys.getsizeof(tfidf_matrix.indptr)

def salvar_indice(tfidf_matrix, vectorizer, caminho_tfidf='indice_tfidf.pkl', caminho_vectorizer='vectorizer.pkl'):
    # Salva a matriz TF-IDF
    joblib.dump(tfidf_matrix, caminho_tfidf)
    # Salva o vetorizador
    joblib.dump(vectorizer, caminho_vectorizer)
    print(f"Índice TF-IDF e Vetorizador salvos em {caminho_tfidf} e {caminho_vectorizer}.")

def carregar_indice(caminho_tfidf='indice_tfidf.pkl', caminho_vectorizer='vectorizer.pkl'):
    # Carrega o índice TF-IDF
    tfidf_matrix = joblib.load(caminho_tfidf)
    # Carrega o vetorizador
    vectorizer = joblib.load(caminho_vectorizer)
    print(f"Índice TF-IDF e Vetorizador carregados de {caminho_tfidf} e {caminho_vectorizer}.")
    return tfidf_matrix, vectorizer

# Função para buscar trecho de texto na base de dados TF-IDF com 1 retorno
def buscar_texto(query, tfidf_matrix, vectorizer):
    # Transforma a consulta no mesmo formato que os documentos
    query_tfidf = vectorizer.transform([query])
    
    # Calcula a similaridade de cosseno entre a consulta e todos os documentos
    similaridade = cosine_similarity(query_tfidf, tfidf_matrix)
    
    # Retorna o índice do documento mais similar
    indice_mais_similar = similaridade.argmax()
    return indice_mais_similar, similaridade[0][indice_mais_similar]

# Função para buscar trecho de texto na base de dados TF-IDF com multiplos retornos
def buscar_texto_multiple(query, tfidf_matrix, vectorizer, limiar, top_n):
    
    # Transformar a query para o formato TF-IDF
    query_tfidf = vectorizer.transform([query])
    
    # Calcular a similaridade de cosseno entre a query e os documentos indexados
    similaridade = cosine_similarity(query_tfidf, tfidf_matrix)
    
    # Ordenar os documentos pela similaridade, do mais relevante para o menos relevante
    indices_ordenados = similaridade.argsort()[0][::-1]
    similaridades_ordenadas = similaridade[0][indices_ordenados]
    
    # Filtra os resultados com base no limiar
    resultados = [
        (indice, similaridade) for indice, similaridade in zip(indices_ordenados, similaridades_ordenadas)
        if similaridade >= limiar
    ]
    
    # Se houver resultados, retorna os top_n documentos
    return resultados[:top_n]

def transforma_dados(diretorio_limpo, diretorio_transformado):

    arquivos = listar_arquivos_em_diretorio(diretorio_limpo)

    nltk.download('punkt_tab')
    nltk.download('stopwords')

    os.makedirs(diretorio_transformado, exist_ok=True)

    for arquivo in arquivos:
        with open(arquivo, 'r', encoding='utf-8') as file:
            pagina = file.read()
        
        #print(pagina[:500])  # Exibe os primeiros 500 caracteres do texto processado
        texto_processado = pre_processar(pagina)
        #print(texto_processado[:500])  # Exibe os primeiros 500 caracteres do texto processado


        dir = os.path.join(diretorio_transformado, os.path.basename(arquivo))
        with open(dir , 'w', encoding='utf-8') as file:
            file.write(texto_processado)

    # TF-IDF

    tfidf_matrix, vectorizer = avaliar_tempo_espaco_indexacao(diretorio_transformado)
    salvar_indice(tfidf_matrix, vectorizer)

    print("Número de termos no vocabulário:", len(vectorizer.get_feature_names_out()))
    vocabulario = vectorizer.get_feature_names_out()

    caminho_arquivo = 'vocabulario.txt'

    # Abre o arquivo no modo de escrita
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        for palavra in vocabulario:
            f.write(palavra + '\n')  # Escreve uma palavra por linha

    print(f'Vocabulário salvo em {caminho_arquivo}')


# LIMPAR DADOS                  ##############################################################################################################

diretorio_origem = os.path.join( 'paginas/A')
diretorio_limpo = os.path.join(os.getcwd(), 'paginas_processadas_n/processadas')
diretorio_transformado = os.path.join(os.getcwd(), 'paginas_processadas_n/transformado/')

# Criar o diretório de destino, se não existir
os.makedirs(diretorio_limpo, exist_ok=True)

# filtrar_limpar_dados( diretorio_origem, diretorio_limpo)


# TRANSFORMAR DADOS           ##############################################################################################################

# transforma_dados(diretorio_limpo, diretorio_transformado)


tfidf_matrix, vectorizer = carregar_indice()
##############################################################################################################################################

# A Fault Line, a Fault Of Mine
# Power Of Persuasion
# Birds Of Prey -- We havent burned these bridges for the last time so i'll get the gas
# You're Not In Love
# Cassandra -- Sorry Cassandra, I misunderstood, now the last day is dawning Some of us wanted
# Imagining My Man -- I'm going to answer protected It can be so hard to forgive It's not what I thought


def main(query):

    # Criar o diretório de destino, se não existir
    #os.makedirs(diretorio_limpo, exist_ok=True)

    
    
    limiar = 0.1
    top_n = 10

    #print("===========================================================================================\nResultados para pesquisa de: ",query)
    resultados = buscar_texto_multiple(query, tfidf_matrix, vectorizer, limiar, top_n)

    arquivos = listar_arquivos_em_diretorio(diretorio_limpo)

    # PARTE COMENTADA ABAIXO É SE QUISER FAZER O PROGRAMA RETORNAR A LISTA DE ARQUIVOS JÁ EM FORMATO DE TEXTO

    pags = []
    links = []
    # Exibe os resultados da busca
    for idx, (indice, sim) in enumerate(resultados):
        print("\n------------------------------------------------------------------------------------------")
        print(f"Resultado {idx + 1}: Documento {indice} com similaridade {sim:.4f}")
        link = "https://www.letras.com/" + os.path.basename(arquivos[indice])[:-4] 
        link = link.replace('_', '/')
        with open(arquivos[indice], 'r', encoding='utf-8') as file:
            primeira_linha = file.readline().strip()
            segunda_linha = file.readline().strip()

            # Concatena as duas linhas, se necessário
            pagina = primeira_linha + '\n' + segunda_linha
            #pagina = file.read()

        links.append(link)
        pags.append(pagina)
    print(links)
    print(pags)
    return pags, links
    #return resultados  # RETORNA LISTA DE ÍNICES
