from bs4 import BeautifulSoup 
import requests
import string
import os
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import time
import json

url = 'https://www.letras.com/letra/Z/artistas.html'

def get_html(url):
    return requests.get(url, allow_redirects=False).text

def get_artistas(letra):

    url = 'https://www.letras.com/letra/' + letra + '/artistas.html'
    
    
    lista_artistas = []
    try: 
        html = get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        ul = soup.find('ul', {'class': 'cnt-list cnt-list--col3'})
        link_artistas = ul.find_all('li')
        for row in link_artistas:
            link_artista = row.find('a').attrs.get('href', '')
            lista_artistas.append(link_artista)
    except Exception as e:
        print("Error: " + str(e))

    return lista_artistas

def get_musicas_de_artista(link_artista):

    link_artista = 'https://www.letras.com' + link_artista

    html = get_html(link_artista)
    lista_musicas = [] 
    artista = ''
    try: 
        soup = BeautifulSoup(html, 'html.parser')
        links_musicas = soup.find_all('a', {'class': 'songList-table-songName font --base --size16'})
        artista = soup.find('h1', {'class': 'textStyle-primary'}).text[9:-5]
        for row in links_musicas:
            link_musica = row.attrs.get('href', '')
            lista_musicas.append(link_musica)
        
    except Exception as e:
        print("Error: " + str(e))
        
 

    return lista_musicas, artista

def get_letra(link_musica):
    link_musica = 'https://www.letras.com' + link_musica

    letra = ''
    title = ''

    try:
        html = get_html(link_musica)

        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1' , {'class': 'textStyle-primary'}).contents[0][9:-5]
        lyrics = soup.find('div', {'class': 'lyric-original'})
        lyrics = lyrics.find_all('p')
        for line in lyrics:
            letra = letra + ' ' + line.text
            #letra.append(line.text)
    except Exception as e:
        print("Error: " + str(e))

    return letra, title

def main():

    letras = list(string.ascii_uppercase)
    letras.append('1')

    lista_artistas = []

    for letter in letras:
        lista_artistas = get_artistas(letter)      
        caminho_nova_links = os.path.join(os.getcwd(), 'links_')
       
       
        if not os.path.exists(caminho_nova_links):
            os.makedirs(caminho_nova_links)


        for artista in lista_artistas:
            lista_musicas = get_musicas_de_artista(artista)
            if len(lista_musicas) > 0:
                
                with open(caminho_nova_links + '\\' + letter +'.txt', 'a') as arquivo:
                    for musica in lista_musicas:
                        if musica[0] == '/':
                            arquivo.write(musica+'\n')


def up_musicas_on_es(musicas, artista_nome):

    es = Elasticsearch(["http://localhost:9200"])

    # Lista de músicas
    
    # Usar a API de bulk para enviar múltiplos documentos de uma vez
    response = helpers.bulk(es, musicas)

    for res in response[1]:
        if res.get('create', {}).get('status') != 201:
            print(f"Failed to index document: {res}")

    # Contar quantos documentos foram indexados com sucesso
    print(f"Total documents indexed: {response[0]}" + '  -  ' + artista_nome )

def salvar_ou_ler_artistas_letra(letra, opcao):
    lista_artistas = []

    if(opcao == 1):

        lista_artistas =  get_artistas(letra)

        with open('lista.txt', 'w', encoding='utf-8') as arquivo:
            for item in lista_artistas:
                arquivo.write(f"{item}\n")
    else:


        with open('lista.txt', 'r', encoding='utf-8') as arquivo:
            lista_artistas = [linha.strip() for linha in arquivo]

    return lista_artistas

def deletar_artistas(lista_artistas):
    try:
        for artista in lista_artistas:

            html = get_html('https://www.letras.com' + artista)
            soup = BeautifulSoup(html, 'html.parser')
            nome_artista = soup.find('h1', {'class': 'textStyle-primary'}).text[9:-5]

            #print(f"\n\nDeletando músicas do artista: {nome_artista}")

            # Busca todas as músicas do artista
            search_query = {
                "query": {
                    "term": {
                        "artist.keyword": nome_artista  # Busca exata pelo nome do artista
                    }
                }
            }


            # Realiza a busca das músicas no Elasticsearch
            search_response = requests.post(
                f"http://localhost:9200/songs/_search?scroll=1m&size=300",
                headers={"Content-Type": "application/json"},
                data=json.dumps(search_query)
            )

            search_data = search_response.json()
            if 'hits' not in search_data or search_data['hits']['total']['value'] == 0:
                #print(f"Nenhuma música encontrada para o artista: {nome_artista}")
                continue

            # Processa os resultados e deleta as músicas
            scroll_id = search_data['_scroll_id']
            
            hits = search_data['hits']['hits']
            
            for hit in hits:
                # Processar os resultados
                if not hits:
                    break

                bulk_delete_body = ""
                for hit in hits:
                    song_id = hit['_id']
                    bulk_delete_body += json.dumps({"delete": {"_index": 'songs', "_id": song_id}}) + "\n"

                # Envia o comando de exclusão em massa
                bulk_response = requests.post(
                    f"http://localhost:9200/songs/_bulk",
                    headers={"Content-Type": "application/x-ndjson"},
                    data=bulk_delete_body
                )
                if bulk_response.status_code != 200:
                    #print(f"Deletadas músicas do artista: {nome_artista}")
                #else:
                    print(f"Erro ao deletar músicas do artista: {nome_artista}")

                # Busca mais resultados, caso haja mais
                scroll_response = requests.post(
                    f"http://localhost:9200/songs/_search/scroll",
                    headers={"Content-Type": "application/json"},
                    data=json.dumps({"scroll": "1m", "scroll_id": scroll_id})
                )
                search_data = scroll_response.json()

    except Exception as e:
        print(str(e))       
                
            
def up_musicas_on_es2(musicas):

    es = Elasticsearch(["http://localhost:9200"])

    # Lista de músicas
    
    # Usar a API de bulk para enviar múltiplos documentos de uma vez
    response = helpers.bulk(es, musicas)

    for res in response[1]:
        if res.get('create', {}).get('status') != 201:
            print(f"Failed to index document: {res}")

    # Contar quantos documentos foram indexados com sucesso
    print(f"Total documents indexed: {response[0]}" )

def main_test2(l):
    
    letras = list(string.ascii_uppercase)
    #letras.append('1')

    letras = [l]

    lista_artistas = []

    for letter in letras:

        lista_artistas = get_artistas(letter)
        count = 0
        musicas = []
        
        for artista in lista_artistas:
            lista_musicas, artista_nome = get_musicas_de_artista(artista)
            if len(lista_musicas) > 0:
                if(count == 50):
                    print(str(len(musicas)))
                    count = 0
                    up_musicas_on_es2(musicas)
                    musicas = []
                    print("Artista:" + '  -  ' + artista_nome)
                    
                count +=1    
                for link_music in lista_musicas:    
                    try:
                        if(link_music[0] == '/'):
                            letra , titulo = get_letra(link_music)
                            musica = {"_index": "songs", "_source": {
                                "title": titulo,
                                "artist": artista_nome,
                                "lyrics": letra,
                                }}
                            musicas.append(musica)
                    except Exception as e:
                        print(str(e)  )
        up_musicas_on_es2(musicas)





inicio = datetime.now()
print(datetime.now())

main_test2('D')

print("Inicio: " + str(inicio))

print("Fim   : " + datetime.now())