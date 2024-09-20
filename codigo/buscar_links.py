from bs4 import BeautifulSoup 
import requests

url = 'https://www.letras.com/letra/Z/artistas.html'

def get_html(url):
    return requests.get(url).text

def get_artista(url):

    html = get_html(url)
    soup = BeautifulSoup(html, 'html.parser')
    ul = soup.find('ul', {'class': 'cnt-list cnt-list--col3'})
    lista_artistas = ul.find_all('li')
    #print(table_rows)

    for row in lista_artistas:
        link_artista = row.find('a').attrs.get('href', '')
        #link_artista = link_artista
        print(link_artista)

#get_artista(url)

link_artista = '/nx-zero/'

def get_musicas_de_artista(link_artista):

    link_artista = 'https://www.letras.com' + link_artista

    html = get_html(link_artista)

    soup = BeautifulSoup(html, 'html.parser')
    links_musicas = soup.find_all('a', {'class': 'songList-table-songName font --base --size16'})
    
    for row in links_musicas:
        link_musicas = row.attrs.get('href', '')
        #link_artista = link_artista
        print(link_musicas)
 
get_musicas_de_artista(link_artista)