# Anna-AI
Magyar AI, akivel hangalapon tudsz beszélni, üzeneteket tud írni, olvasni és összefoglalni Discord segítségével!

# Kompatibilítás
Jelenleg **csak MacOS-el és Linux-al** kompatibilis! Az alábbi parancsok is csak azokon a rendszereken működik!

A Windows kompatibilításon még dolgozok!

# Setup
## Klónold le a projektet
```
git clone https://github.com/cablesalty/Anna-AI
```
*(Vagy töltsd le .zip-ben és csomagold ki)*

## Szükséges programok letöltése
A szükséges Python csomagok telepítéséhez ezt a parancsot használd:
```
pip3 install -r requirements.txt
```
Emellett még szükséged lesz az alábbi programokra:
- `Ansiweather` - Időjárás lekéréséhez
- `SoX` - (**So**und e**X**change) - Audio lejátszásához
### MacOS:
```
brew install ansiweather sox
```
*(szükséges: [homebrew](https://brew.sh))*

### Debian Linux (Ubuntu, stb...):
```
sudo apt-get install ansiweather sox
```

### Arch Linux:
```
yay -S ansiweather sox
```

## Helyes mikrofon beállítása
A helyes mikrofon beállításához futtasd le a `get-mics.py` fájlt.
```
python3 get-mics.py
```
*(szükséges: `pip3 install speechrecognition`)*
### Ilyesmi kimentet fogsz kapni
```
Mikrofon "Pateszko Microphone" megtalálva. ID `Microphone(device_index=0)`
Mikrofon "Patrik’s AirPods Pro" megtalálva. ID `Microphone(device_index=1)`
Mikrofon "Patrik’s AirPods Pro" megtalálva. ID `Microphone(device_index=2)`
Mikrofon "MacBook Pro Microphone" megtalálva. ID `Microphone(device_index=3)`
Mikrofon "MacBook Pro Speakers" megtalálva. ID `Microphone(device_index=4)`
```
Ha például a MacBook mikrofonját akarod kiválasztani, akkor a neked **mikrofon 3** kell. **De csak ebben a példában 3 az ID-je! Futtasd le magad a scriptet!**

### Mikrofon beállítása
Nyisd meg a `main.py` fájlt, és keresd meg ezt a kódsort *(a fájl elején/tetején lesz)*:
```py
#* Válaszd ki a helyes mikrofon ID-t!
#* A README fájl ezt leírja!
micid = 0
```
Itt írd át a micid értékét arra a számra, amit előzöleg kaptál a `get-mics.py` fájlból!

## OpenAI API Kulcs megadása
A futtatáshoz szükséged van egy OpenAI kulcsra.
### Menj fel az [OpenAI fejlesztő portálra](https://platform.openai.com/)
Nyiss egy böngészőablakot/tabot, és menj fel az [OpenAI fejlesztői portálra](https://platform.openai.com/).
**Ehhez be kell jelentkezned az OpenAI fiókodba.** Ugyan abba a fiókba is bejelentkezhetsz, amivel a ChatGPT-t használod. Ha még nincs fiókod, hozz létre egyet.

### API Kulcs létrehozása
Belépés után kattincs az oldalsó menüben az `API Keys` menüpontra. *(Lakat ikon)*

Az `API Keys` menüben kattincs a `Create new secret key` gombra, majd nevezd el az API Kulcsodat, és kattints a `Create` gombra.Előfordulhat hogy egy CAPTCHA-t ki kell töltened.

Miután létrehoztad a kulcsodat **Másold ki egy fájlba**. Az a lényeg, hogy tárold valahol ezt a kulcsot, mert **miután bezáraod az ablakot, nem tudod megtekinteni/kimásolni újra a kulcsot**.

### API Kulcs betáplálása
Miután biztonságos helyre elmentetted az API Kulcsodat, hozz létre egy változót a parancssorban.

```
export OPENAIKEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
*(Cseréld ki a kulcsot a sajátodra. "sk"-val kezdődik.)*

### Fontos megjegyezni:
- A változók amiket megadsz parancssorban/terminálban **NEM** lesznek elmentve. Ez azt jelenti, hogyha bezárod a parancssor-t/terminal-t, akkor a beállított változó el fog veszni! Ezért fontos, hogy a tokenedet egy külön fájlba tárold!

- Csak akkor fog működni a program, ha ugyan abból a parancssorból indítod el a programot, ahol létrehoztad a változót.

## Discord token megadása
Ha szeretnél üzeneteket olvasni, írni és összefoglalni az AI-al, akkor be kell táplálnod a Discord tokenedet.

### Jelentkezz be a Discord ba a discord.com-on
Nyiss egy új böngészőablakot/tabot, és jelentkezz be a [Discord oldalán](https://discord.com). A következő lépéseknél **a Discord asztali alkalmazása NEM fog működni!**

### Fejlesztői ezközök megnyitása
Nyisd meg a böngésződ fejlesztői ezközeit. Mivel a Discord oldalán nem működik a *"Jobb Click>Inspect Element"*, billentyűparancsal kell megnyitnod a fejlesztői ezközöket. Nézz utánna, hogy a te böngésződben hogy lehet megnyitni!

### Token megszerzése
Miután megnyitottad a fejlesztői ezközöket, kattints a `Console` fülre. Így átlépsz a JavaScript konzol-ba.

Miután megnyitod a JavaScript konzolt, egy folyamatosan megjelenő figyelmeztetéssel találod szembe magad. Ezt a figyelmeztetést nyugottan ignorálhatod, mivel ez nem token lopó. Ha nem bízol bennem, vagy nem vagy biztos abban hogy mit csinál ez a script, akkor nyugodtan kihagyhatod ezt a fejezetet, és továbbugorhatsz a [következő lépésre](#program-futtatása).


Miután megnyitottad a JavaScript konzolt, másold be ezt a kódot a konzolba:
```js
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

Ha nem vagy biztos abban hogy mit csinál a kód, akkor itt van egy "szebb" változata:
```js
(
    webpackChunkdiscord_app.push(
        [
            [''],
            {},
            e => {
                m=[];
                for(let c in e.c)
                    m.push(e.c[c])
            }
        ]
    ),
    m
).find(
    m => m?.exports?.default?.getToken !== void 0
).exports.default.getToken()
```

**Ez a script semmilyen fajta módon nem lopja el a tokenedet!** Ha nem bízol bennem, nyugodtan kihagyhatod ezt a fejezetet, és továbbugorhatsz a [következő lépésre](#program-futtatása).

### Discord token betáplálása
Miután megszerezted a Discord tokenedet, hozz létre egy változót a parancssorban.

```
export DISCORDTOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
*(Cseréld ki a token-t a sajátodra.)*

### Fontos megjegyezni:
- A változók amiket megadsz parancssorban/terminálban **NEM** lesznek elmentve. Ez azt jelenti, hogyha bezárod a parancssor-t/terminal-t, akkor a beállított változó el fog veszni! Ha a jövőben is szeretnéd a tokenedet lekérni az előző lépések végigkövetése nélkül, mentsd el a tokenedet egy fájlba!

- Csak akkor fog működni a program, ha ugyan abból a parancssorból indítod el a programot, ahol létrehoztad a változót.


## Discord felhasználóneved megadása
Ha megadtad a tokenedet, akkor meg kell adnod a saját Discord felhasználónevedet.

Nyisd meg a `main.py` fájl-t, és keresd meg ezt a kódsort (a `config` class-ban lesz):
```py
# Discord felhasználóneved ("@" nélkül)
mydcusername = "valaki"
```
Cseréld ki a "mydcusername" értékét a saját Discord felhasználónevedre (@ nélkül)

A Discord felhasználónevedet a profilodra kattintva tudod megtekinteni.

![Discord profil](https://i.imgur.com/Fa39Xuz.png)

Miután rákattintottál, látni fogod a felhasználónevedet (A képen a nyíl mutatja).

![Discord profil kártya](https://i.imgur.com/DgKgbqC.png)

## A Jelenlegi Városod megadása
Az időjárás funkciónak a helyes működéséhez meg kell adnod a városodat.

Nyisd meg a `main.py` fájl-t, és keresd meg ezt a kódsort (a `config` class-ban lesz):
```py
# A városod
# Az időjáráshoz szükséges
mycity = "Budapest"
```

Cseréld ki a `mycity` értékét a városod nevére.

# Program futtatása
Ha mindennel készen vagy, akkor csak futtasd a programot
```
python3 main.py
```

# További konfigurálás
Ha tovább szeretnéd konfigurálni az AI-t akkor itt van pár instrukció!

## AI Modell Váltása
Ha van OpenAI credited és szeretnél egy másik generatív AI modellre váltani, akkor így tudod megtenni:

Nyisd meg a `main.py` fájl-t, és keresd meg ezt a kódsort (a `config` class-ban lesz):
```py
# AI Modell
# OpenAI modell váltása
# Nézd meg a dokumentációt az OpenAI oldalán,
# vagy olvasd el a README fájl-t.
aimodel = "gpt-3.5-turbo"
```
Változtasd meg az `aimodel` változó értékét egy helyes modell nevére.

Az AI modell típusok nevei megtalálhatók az [OpenAI Dokumentációjában](https://platform.openai.com/docs/models/overview).

## Felhasználói adatok
Ha szeretnéd egy kicsit testreszabni az AI-t, akkor meg tudod változtatni a `userdata.txt` fájl-t. Ebbe a fájlba hasonló adatokat tudsz beírni:

```
Név: Végh Béla
Születési dátum: 2001/09/11
```

Ennek a fájlnak a segítségével már az AI tudja az életkorodat, nevedet, stb... és így még célzottabb válaszokat tud neked adni

**Figyelem:** Nagyon személyes adatokat ne adj meg! Az összes szöveget az OpenAI fogja feldolgozni. Amit nem szeretnél hogy tudjanak, ne mondd el az AI-nak!