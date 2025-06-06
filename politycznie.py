import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from nltk.util import ngrams
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

def wczytaj_stopwords(plik):
    try:
        with open(plik, encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"❌ Nie znaleziono pliku: {plik}")
        return set()

class PolitykaScraperConsole:
    def __init__(self, liczba_stron=5, plik_stopwordow="stop_words_polish.txt",
                 base_url="", selektor_tytulu=""):
        self.headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "pl-PL,pl;q=0.9"
        }
        self.base_url = base_url
        self.selektor_tytulu = selektor_tytulu
        self.tytuly = []
        self.liczba_stron = liczba_stron
        self.stopwords = wczytaj_stopwords(plik_stopwordow)

    def pobierz_html(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Błąd pobierania: {url} [{response.status_code}]")
            return ""

    def ekstrakcja_tytulow(self, html):
        soup = BeautifulSoup(html, "html.parser")
        artykuly = soup.select(self.selektor_tytulu)
        for element in artykuly:
            tytul = element.get_text(strip=True)
            if len(tytul) > 35:
                self.tytuly.append(tytul)

    def scrapuj_wiele_stron(self):
        for i in range(1, self.liczba_stron + 1):
            url = f"{self.base_url}{i}"
            html = self.pobierz_html(url)
            self.ekstrakcja_tytulow(html)
        print(f"✅ Zebrano {len(self.tytuly)} tytułów.\n")

    def policz_slowa(self):
        text = " ".join(self.tytuly).lower()
        text = re.sub(r"[^\w\s]", "", text)
        words = text.split()
        return Counter(word for word in words if word not in self.stopwords)

    def pokaz_wordcount(self, counter, ile=20):
        print("\n📊 Najczęstsze słowa:")
        for word, count in counter.most_common(ile):
            print(f"{word:<20} {count}")

    def pokaz_frazy(self, counter, n=2, ile=20):
        text = " ".join(self.tytuly).lower()
        text = re.sub(r"[^\w\s]", "", text)
        words = [w for w in text.split() if w not in self.stopwords]
        ngramy = Counter(ngrams(words, n))
        print(f"\nNajczęstsze {n}-gramy:")
        for ngram, count in ngramy.most_common(ile):
            print(" ".join(ngram), "-", count)
        return ngramy

#### wizaluzalizacje
def rysuj_chmure_slow(counter, tytul="Chmura słów"):
    wordcloud = WordCloud(width=1200, height=600, background_color="white").generate_from_frequencies(counter)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(tytul)
    plt.show()

def rysuj_słupki(counter, top_n=20, tytul="Top słowa"):
    dane = counter.most_common(top_n)
    slowa, liczby = zip(*dane)
    plt.figure(figsize=(12, 6))
    plt.bar(slowa, liczby)
    plt.xticks(rotation=45)
    plt.title(tytul)
    plt.tight_layout()
    plt.show()

def venn_porownanie(c1, c2, c3, labels=["Portal1", "Portal2", "Portal3"]):
    s1, s2, s3 = set(c1), set(c2), set(c3)
    plt.figure(figsize=(8, 8))
    venn3([s1, s2, s3], set_labels=labels)
    plt.title("Wspólne i unikalne słowa")
    plt.show()

def wypisz_wspolne_i_unikalne(c1, c2, c3, labels=["Portal1", "Portal2", "Portal3"]):
    s1, s2, s3 = set(c1), set(c2), set(c3)

    wspolne = s1 & s2 & s3
    tylko1 = s1 - s2 - s3
    tylko2 = s2 - s1 - s3
    tylko3 = s3 - s1 - s2

    print(f"\n🔗 Wspólne słowa ({labels[0]}, {labels[1]}, {labels[2]}):")
    for w in sorted(wspolne):
        print("-", w)
def rysuj_bigramy(scraper, top_n=20, tytul="Top bigramy"):
    text = " ".join(scraper.tytuly).lower()
    text = re.sub(r"[^\w\s]", "", text)
    words = [w for w in text.split() if w not in scraper.stopwords]
    bigramy = Counter(" ".join(t) for t in ngrams(words, 2))

    dane = bigramy.most_common(top_n)
    frazy, liczby = zip(*dane)

    plt.figure(figsize=(12, 6))
    plt.bar(frazy, liczby)
    plt.xticks(rotation=45, ha='right')
    plt.title(tytul)
    plt.tight_layout()
    plt.show()

##wyniki
scraper1 = PolitykaScraperConsole(
    liczba_stron=5,
    plik_stopwordow="stop_words_polish.txt",
    base_url="https://tvrepublika.pl/kategoria/Polityka?page=",
    selektor_tytulu="h2"
)

scraper2 = PolitykaScraperConsole(
    liczba_stron=5,
    plik_stopwordow="stop_words_polish.txt",
    base_url="https://wiadomosci.wp.pl/tag/polityka/?page=",
    selektor_tytulu="h2"
)

scraper3 = PolitykaScraperConsole(
    liczba_stron=5,
    plik_stopwordow="stop_words_polish.txt",
    base_url="https://wpolsce24.tv/polska/strona,",
    selektor_tytulu="h3"
)

#Scrapowanie
for scraper in [scraper1, scraper2, scraper3]:
    scraper.scrapuj_wiele_stron()

# Analiza i wizualizacja
c1 = scraper1.policz_slowa()
c2 = scraper2.policz_slowa()
c3 = scraper3.policz_slowa()

# WordCloud + słupki
rysuj_chmure_slow(c1, "TV Republika – chmura słów")
rysuj_słupki(c1, tytul="TV Republika – top słowa")

rysuj_chmure_slow(c2, "WP – chmura słów")
rysuj_słupki(c2, tytul="WP – top słowa")

rysuj_chmure_slow(c3, "WPolsce24 – chmura słów")
rysuj_słupki(c3, tytul="WPolsce24 – top słowa")

# Venn
venn_porownanie(c1, c2, c3, labels=["Republika", "WP", "WPolsce24"])
wypisz_wspolne_i_unikalne(c1, c2, c3, labels=["Republika", "WP", "WPolsce24"])

rysuj_bigramy(scraper1, tytul="TV Republika – top bigramy")
rysuj_bigramy(scraper2, tytul="WP – top bigramy")
rysuj_bigramy(scraper3, tytul="WPolsce24 – top bigramy")

