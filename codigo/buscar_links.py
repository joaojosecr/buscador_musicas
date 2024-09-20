from bs4 import BeautifulSoup 
import requests
import string
import os
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

    lista_musicas = []
    for row in links_musicas:
        link_musica = row.attrs.get('href', '')
        #link_artista = link_artista
        lista_musicas.append(link_musica)
    
    return lista_musicas

def main():

    letras = list(string.ascii_uppercase)
    letras.append('1')

    lista_artistas = []

    #for letter in letras:
    lista_artistas = get_artistas('A')      # ALTERAR LETRA 'A' PARA LETTER DENTRO DO FOR 
    caminho_nova_links = os.path.join(os.getcwd(), 'links')
    # Verifica se a nova pasta já existe, caso contrário, cria a pasta
    if not os.path.exists(caminho_nova_links):
        os.makedirs(caminho_nova_links)

    for artista in lista_artistas:
        lista_musicas = get_musicas_de_artista(artista)
        if len(lista_musicas) > 0:
            #caminho_arquivo = caminho_nova_pasta + '\\' + artista[1:-1] + '.txt'
            with open(caminho_nova_links + '\\A.txt', 'a') as arquivo:
                for musica in lista_musicas:
                    if musica[0] == '/':
                        arquivo.write(musica+'\n')




main()

