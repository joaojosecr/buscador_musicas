from bs4 import BeautifulSoup 
import requests
import os
from datetime import datetime
import string

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
    try: 
        soup = BeautifulSoup(html, 'html.parser')
        links_musicas = soup.find_all('a', {'class': 'songList-table-songName font --base --size16'})
        for row in links_musicas:
            link_musica = row.attrs.get('href', '')
            lista_musicas.append(link_musica)
        
    except Exception as e:
        print("Error: " + str(e))
        
 

    return lista_musicas

def main():

    letras = list(string.ascii_uppercase)
    letras.append('1')

    for letter in letras:
        lista_artistas = get_artistas(letter)      

        caminho_paginas = os.path.join(os.getcwd(), 'paginas')
        
        if not os.path.exists(caminho_paginas):
            os.makedirs(caminho_paginas)

        caminho_letra = os.path.join(caminho_paginas, letter)

        if not os.path.exists(caminho_letra):
            os.makedirs(caminho_letra)
        
        with open(caminho_letra + '\\lista_' + letter + '.txt', 'w', encoding='utf-8') as arquivo:
            for item in lista_artistas:
                arquivo.write(f"{item}\n")

        for artista in lista_artistas:
            lista_musicas = get_musicas_de_artista(artista)        
            
            for musica in lista_musicas:
                try:
                    if(musica[0] == '/'):
                        caminho_nome_arquivo = caminho_letra + '\\' + musica[1:(len(musica)-1)].replace('/', '_')+'.html'
                        html = get_html('https://www.letras.com'+musica) 
                        with open(caminho_nome_arquivo, 'w', encoding="utf-8") as arquivo:
                            arquivo.write(html)
                except Exception as e:
                    print(e)

# inicio = datetime.now()
# print("Inicio: " + str(inicio))

# main()

# print("Fim   : " + str(datetime.now()))



