import os
from bs4 import BeautifulSoup

# Diretórios de origem e destino
diretorio_destino = os.path.join(os.getcwd(), 'paginas_processadas/A')
diretorio_origem = os.path.join(os.getcwd(), 'paginas/A')

# Criar o diretório de destino, se não existir
os.makedirs(diretorio_destino, exist_ok=True)

def processar_arquivo(caminho_arquivo, caminho_destino):
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

# Iterar pelos arquivos no diretório de origem
for nome_arquivo in os.listdir(diretorio_origem):
    caminho_arquivo = os.path.join(diretorio_origem, nome_arquivo)
    caminho_destino = os.path.join(diretorio_destino, nome_arquivo)
    
    if os.path.isfile(caminho_arquivo):  # Certificar que é um arquivo
        processar_arquivo(caminho_arquivo, caminho_destino)