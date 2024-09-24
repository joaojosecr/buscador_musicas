from bs4 import BeautifulSoup 
import requests
import string
import os
from elasticsearch import Elasticsearch, helpers
from datetime import datetime
import time

url = 'https://www.letras.com/letra/Z/artistas.html'

def get_html(url):
    return requests.get(url).text

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
        print("Error: " + e)

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
        print("Error: " + e)
        
 

    return lista_musicas, artista

def get_letra(link_musica):
    link_musica = 'https://www.letras.com' + link_musica

    letra = ''
    titulo = ''

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
        print("Error: " + e)

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

def main_test():
    
    letras = list(string.ascii_uppercase)
    letras.append('1')

    lista_artistas = []

    lista_artistas = get_artistas('A')
    count = 0

    for artista in lista_artistas:
        lista_musicas, artista_nome = get_musicas_de_artista(artista)
        musicas = []
        if len(lista_musicas) > 0:
            if(count == 30):
                print("\n ------ PAUSA ----- \n")
                count = 0
                time.sleep(200)
            count +=1 
            for link_music in lista_musicas:    
                if(link_music[0] == '/'):
                    letra , titulo = get_letra(link_music)
                    musica = {"_index": "songs", "_source": {
                        "title": titulo,
                        "artist": artista_nome,
                        "lyrics": letra,
                        }}
                    musicas.append(musica)

              
            up_musicas_on_es(musicas, artista_nome)



def main_test2():
    

    artistas = []
    with open('z.txt','r')as arquivo:
        for line in arquivo:
            artistas.append(line.strip())

    count = 0
    for artista in artistas:
        lista_musicas, artista_nome = get_musicas_de_artista(artista)
        musicas = []
        if len(lista_musicas) > 0:
            if(count == 30):
                print("\n ------ PAUSA ----- \n")
                count = 0
                time.sleep(200)
            count +=1 
            for link_music in lista_musicas:    
                if(link_music[0] == '/'):
                    letra , titulo = get_letra(link_music)
                    musica = {"_index": "songs", "_source": {
                        "title": titulo,
                        "artist": artista_nome,
                        "lyrics": letra,
                        }}
                    musicas.append(musica)

              
            up_musicas_on_es(musicas, artista_nome)

print(datetime.now())

main_test()

print(datetime.now())


