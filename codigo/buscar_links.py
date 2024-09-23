from bs4 import BeautifulSoup 
import requests
import string
import os
from elasticsearch import Elasticsearch
from datetime import datetime

url = 'https://www.letras.com/letra/Z/artistas.html'

def get_html(url):
    return requests.get(url).text

def get_artistas(letra):

    url = 'https://www.letras.com/letra/' + letra + '/artistas.html'
    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    ul = soup.find('ul', {'class': 'cnt-list cnt-list--col3'})
    link_artistas = ul.find_all('li')
    lista_artistas = []
    for row in link_artistas:
        link_artista = row.find('a').attrs.get('href', '')
        lista_artistas.append(link_artista)

    return lista_artistas

def get_musicas_de_artista(link_artista):

    link_artista = 'https://www.letras.com' + link_artista

    html = get_html(link_artista)

    soup = BeautifulSoup(html, 'html.parser')
    links_musicas = soup.find_all('a', {'class': 'songList-table-songName font --base --size16'})
    artista = soup.find('h1', {'class': 'textStyle-primary'}).text[9:-5]
    lista_musicas = []
    for row in links_musicas:
        link_musica = row.attrs.get('href', '')
        lista_musicas.append(link_musica)
    
    return lista_musicas, artista

def get_letra(link_musica):
    link_musica = 'https://www.letras.com' + link_musica

    html = get_html(link_musica)

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find('h1' , {'class': 'textStyle-primary'}).contents[0][9:-5]
    lyrics = soup.find('div', {'class': 'lyric-original'})
    lyrics = lyrics.find_all('p')
    letra = ''
    for line in lyrics:
        letra = letra + ' ' + line.text
        #letra.append(line.text)
    
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


def main_test():
    
    musicas = []
   
    lista_musicas, artista = get_musicas_de_artista('/mamonas-assassinas/')
    
    for link_music in lista_musicas:
        letra,titulo = get_letra(link_music)
        musica = {"_index": "songs", "_source": {
            "title": titulo,
            "artist": artista,
            "lyrics": letra,
            }}
        musicas.append(musica)
    
    return musicas


print(datetime.now())

m = main_test()

print(datetime.now())

def set_musica_on_es(artista, titulo, letra):
    es = Elasticsearch(["http://localhost:9200"])  # Substitua pela URL do seu Elasticsearch

    # Dados da música que você quer enviar
    musica = {
        "title": titulo,
        "artist": artista,
        "lyrics": letra,
    }

    # Enviar a música para o índice 'songs'
    response = es.index(index="songs", body=musica)

    # Verificar a resposta
    print(response) 