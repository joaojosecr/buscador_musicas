import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer
from whoosh import index
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

nltk.download('punkt')
nltk.download('stopwords')

# Inicializar stemmer e lista de stopwords
stemmer = RSLPStemmer()
stop_words = set(stopwords.words('portuguese'))

# Diretório onde estão os arquivos
caminho_diretorio = '/paginas/a'
arquivo_lista_processados = 'arquivos_processados.txt'

# Função para carregar a lista de arquivos já processados
def carregar_arquivos_processados(caminho):
    if os.path.exists(caminho):
        with open(caminho, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())
    return set()

# Função para salvar a lista de arquivos processados
def salvar_arquivos_processados(lista, caminho):
    with open(caminho, 'w', encoding='utf-8') as file:
        file.write("\n".join(lista))

# Função para pré-processar um texto
def preprocessar_texto(texto):
    tokens = word_tokenize(texto.lower())
    tokens_processados = [stemmer.stem(word) for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(tokens_processados)

# Definir o esquema para o índice
schema = Schema(id=ID(stored=True), content=TEXT)

# Criar o diretório para o índice
indice_dir = "indice_incremental"
if not os.path.exists(indice_dir):
    os.mkdir(indice_dir)

# Criar ou abrir o índice
if not index.exists_in(indice_dir):
    ix = index.create_in(indice_dir, schema)
else:
    ix = index.open_dir(indice_dir)

# Carregar a lista de arquivos já processados
arquivos_processados = carregar_arquivos_processados(arquivo_lista_processados)

# Função para indexar arquivos incrementais
def indexar_incremental(diretorio, ix, arquivos_processados):
    novos_processados = set(arquivos_processados)
    with ix.writer() as writer:
        for nome_arquivo in os.listdir(diretorio):
            if nome_arquivo in arquivos_processados:
                continue  # Ignorar arquivos já processados
            
            caminho = os.path.join(diretorio, nome_arquivo)
            if os.path.isfile(caminho):
                with open(caminho, 'r', encoding='utf-8') as file:
                    texto = file.read()
                    texto_processado = preprocessar_texto(texto)
                    writer.add_document(id=nome_arquivo, content=texto_processado)
                    novos_processados.add(nome_arquivo)
                    print(f"Arquivo '{nome_arquivo}' processado e indexado.")
    
    # Atualizar a lista de arquivos processados
    salvar_arquivos_processados(novos_processados, arquivo_lista_processados)
    print("Indexação incremental concluída.")

# Indexar os arquivos de forma incremental
indexar_incremental(caminho_diretorio, ix, arquivos_processados)
