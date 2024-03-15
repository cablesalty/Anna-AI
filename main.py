# Anna-AI (https://github.com/cablesalty/Anna-AI) Main File. 
#
# Anna-AI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Anna-AI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "cablesalty"

# Könyvtárak.
import os
import sys
from gtts import gTTS as gtts
import speech_recognition as sr
import time
from openai import OpenAI
import datetime
import json
import wave
import struct
import requests
import subprocess
import ast
import threading

# TODO: Ezen konfigurációk áthelyezése a config class-ba
#* Válaszd ki a helyes mikrofon ID-t!
#* A README fájl ezt leírja!
micid = 0

voiceactivated = False
allowFollowUpQuestions = False

followupquestion = False

#* OpenAI API Kulcs megadása
#* Szükség lesz az OpenAI tokenedre a futtatáshoz.
#
# Indítás előtt állíts be egy változót. (ugyan azzal a parancssorral
# kell elindítanod a programot)
# Linux/Mac:   export OPENAIKEY=<token>
# Windows:     set OPENAIKEY=<token>
client = OpenAI(api_key=os.environ.get("OPENAIKEY"))

class config:
    volume = 1 # SFX és beszéd hangerő

    # Ezek automatikusan változni fognak a program futásakor.
    #* Ne változtasd meg!
    last_ai_response = None
    last_user_question = None
    new_messengers = []
    new_messages = []
    listdata = ""
    memory = ""
    default_messages=[]
    is_getting_ready = True
    #* Ne változtasd meg!


    # Legacy hang: Ha Igazra (True-ra) van állítva, akkor a Google TTS-t fogja használni. 
    # Ez az ajánlott, mivel az OpenAI hangmodelle nagyon megakad a számokban
    legacy_voice = True


    # Üzenetek megerősítése: Üzenetküldéskor felolvassa az AI az üzenetedet és megkérdezi 
    # hogy biztos elküldje e azt. Ajánlott, hátha a Speech to Text félreért. 
    confirm_messages = True


    # Discord felhasználóneved ("@" nélkül)
    mydcusername = "valaki"


    # AI Modell
    # OpenAI modell váltása
    # Nézd meg a dokumentációt az OpenAI oldalán,
    # vagy olvasd el a README fájl-t.
    aimodel = "gpt-3.5-turbo"


    # A városod
    # Az időjáráshoz szükséges
    mycity = "Budapest"


    #* Discord token megadása
    # Szükség lesz a Discord tokenedre, ha üzenetet szeretnél írni vagy
    # olvasni az AI segítségével.
    #
    #* A tokened nem lesz megosztva, még az OpenAI-al sem!
    #
    # Ha szeretnéd megadni a tokenedet, állíts be egy változót indítás
    # előtt a parancssorban. (ugyan azzal a parancssorral kell
    # elindítanod a programot)
    # Linux/Mac:   export DISCORDTOKEN=<token>
    # Windows:     set DISCORDTOKEN=<token>
    discord_token = os.environ.get("DISCORDTOKEN")

    # Telefonkönyv: Név és DM csatorna ID megadásával meg tudod mondani
    # az AI nak hogy hova küldjön üzeneteket. Kövesd a szintaxis-t.
    phonebook = {
        # Szintaxis:
        # "név": "Discord DM csatorna ID"
        # Az AI név szerint fogja beazonosítani a személyt.
    }


# Külön lista az új üzeneteknek.
#* Ne változtass ezen!
messages = config.default_messages

# -------------------- AI főfunkció --------------------
# Ez a funkció csinál kérelmet az OpenAI felé, és dolgozza
# fel a válaszokat.
# ------------------------------------------------------
def ai(prompt, last_response=None, last_user_question=None):
    global client
    # TODO: Új class létrehozása amibe a messages megy.
    global messages

    # Debug
    print(config.default_messages)
    print(messages)

    # Üzenetek lista duplikálása
    rnmessages = []
    rnmessages.extend(messages)

    # Névjegyek megszerzése
    # A nevek az AI-nak lesz betáplálva, ha félreért valamit vagy
    # ragozod az egyik névjegy nevét, akkor is értse.
    contactnamelist = ""
    for name in config.phonebook:
        contactnamelist = contactnamelist + ", " + name
    

    # Ideiglenes változók betáplálása
    # Ezek kellenek az AI-nak hogy tudja a:
    # - Névjegyzék tagjait
    # - Pontos időt
    # - Időjárást
    # - Azt amit mondasz neki.
    rnmessages.append({"role": "system", "content": "A névjegyzék tagjai: " + contactnamelist})    
    rnmessages.append({"role": "system", "content": "A jelenlegi pontos idő " + str(datetime.datetime. now().strftime("%H:%M")) + ", a dátum pedig " + str(datetime.datetime.now().strftime("%Y %m %d"))})
    rnmessages.append({"role": "system", "content": "A hely és hőfok: " + subprocess.check_output(["sh", "ansiweather", "-l", config.mycity, "-u", "metric", "-a", "false"]).decode()})
    rnmessages.append({"role": "user", "content": prompt})

    # Az üzeneted hozzáadása a hosszúlistához.
    # A hosszúlista kérelmeket és AI válaszokat tárol. Ez lehetővé
    # teszi az AI-nak hogy tudjon régebbi üzeneteket keresni, és
    # rájuk válaszolni. Ide nem mentődnek az ideiglenes adatok.
    messages.append({"role": "user", "content": prompt})
    threading.Thread(target=savetomemory).start()

    # Elválasztóvonal nyomtatása
    print("-"*20)
    print()

    # Kérelem nyomtatása debug miatt
    for obj in messages[2:]:
        print(obj)
    print()
    for obj in rnmessages[2:]:
        print(obj)

    #* Válasz kérése
    completion = client.chat.completions.create(
        model=config.aimodel,
        messages=rnmessages
    )

    # Válasz kiírása
    print("-"*20)
    print(vars(completion.choices[0].message))
    print("-"*20)

    # Utolsó válasz és kérdés hozzáadása egy másik ideiglenes listához.
    config.last_ai_response = vars(completion.choices[0].message)["content"]
    config.last_user_question = prompt

    # Válaszból a szöveg kihúzása
    response = vars(completion.choices[0].message)["content"]

    # Parancsok
    # Az AI-nak be van táplálva, ha "__" (dupla alsóvonal)
    # kezdi az üzenetét akkor az egy parancs. Ez teszi lehetővé
    # az AI nak az üzenetek írását és olvasását, stb...
    if response.lower().startswith("_"):
        print("Parancs!")

        # Üzenet írása
        if response.lower().startswith("_msg"):
            print("Parancs típus: Üzenet")

            # Adatok lekérése
            data = response.split('"') # Összes adat, ebből dolgozik.
            recipient = data[1].lower() # Címzett
            message = data[3] # Üzenet

            # Adatok kiírása (debug)
            print(data)
            print(recipient)
            print(message)

            # Megnézzük, hogy a címzett benne van e a
            # telefonkönyvünkben.
            if recipient not in config.phonebook:
                print("HIBA: Címzett nincs a telefonkönyvedben..")
                ttshandler(recipient + " nincs a névjegyzékedben.")
            else:
                print("Címzett megtalálva a névjegyzékedben.")

                # Üzenetküldés megerősítése
                # Ha az AI félreértene valamit, vagy meggondoltad magad
                # az üzenetküldés kapcsán, akkor itt meg tudod mondani az AI-nak
                # hogy mégse küldje el. Ezt a funkciót ki tudod kapcsolni a
                # konfigurációban. (config.confirm_messages)
                while True:
                    ttshandler("Az üzeneted " + recipient + " számára azt mondja: '" + message + "'. Elküldhetem?")
                    confirm = oldstt()
                    if "igen" in confirm:

                        # Mégegyszer leellenőrizzük azt, hogy a felhasználó
                        # biztos elszeretné e küldeni az üzenetet. Ez az
                        # utolsó ellenőrzés arra figyel ha a felhasználó
                        # valami ilyesmit mond:
                        # "Igen ne mégse küld el"
                        if "ne" not in confirm:
                            print("Üzenetküldés megerősítve.")

                            # A címzett csatorna ID-jának lekérése
                            recipientid = config.phonebook[recipient]
                            print(recipientid) # Debug

                            # Szükséges adatok létrehozása
                            msgheader = {"authorization": config.discord_token, "user-agent": "Anna-AI/1.0 (https://github.com/cablesalty/Anna-AI)"}
                            msgdata = {"content": message}

                            # Kérelem elküldése a Discordnak (V9 API)
                            r = requests.post("https://discord.com/api/v9/channels/" + recipientid + "/messages", data=msgdata, headers=msgheader)
                            print(r.status_code)

                            # Megnézzük, hogy sikerült e az üzenetküldés
                            if r.status_code == 200:
                                print("Küldés sikeres!")
                                ttshandler("Az üzenet sikeresen el lett küldve.")
                            else:
                                print("HIBA: Küldés SIKERTELEN!")
                                ttshandler("Az üzenetküldés sikertelen.")
                            
                            return ""
                        else:
                            print("Üzenetküldés megszakítva. (2)")
                            return "Az üzenetküldés megszakítva."
                    elif "nem" in confirm:
                        print("Üzenetküldés megszakítva. (1)")
                        return "Az üzenetküldés megszakítva."
                    else:
                        # Ha a felhasználó mást mond az "igen" vagy "nem" helyett, akkor
                        # az AI újrafogalmazza az üzenetet a felhasználó kérései alapján
                        # és visszatér az ismétlés tetejére.
                        message = ai("Kérlek szerkezd meg és írd újra ezt az üzenetet:\n" + message + "\n\nS következő parancsok és tényezők alapján: '" + confirm + "'.\n\nA te válaszod csak az újra írt üzenet legyen. Mással válaszolni, az üzenetet körülírni tilos! A felhasználó által adott preferenciák és tényezők alapján kell az üzenetet megformáznod úgy, hogy az a tényezőknek megfeleljen! Csak az újraformázott üzenettel válaszolhatsz!")

        # Új üzenetek megtekintése parancs
        # Ha üzeneteket szeretnél olvasni és összefoglaltatni az
        # AI-al, akkor csak annyit kell tőle kérdezned hogy
        # "vannak e új üzeneteim"
        elif response.lower().startswith("_chkmessages"):
            # Debug
            print(config.new_messengers)
            print(config.new_messages)

            # Megnézzük, hogy van e új üzenetet egy lista szerint.
            # Ez a lista folyamatosan frissül a háttérben, és egy
            # értesítés hangot kapsz ha van üzeneted.
            if len(config.new_messages) == 0:
                return "Jelenleg nincs új üzeneted."

            # AI kérelem az üzenetek összefoglalására (üzenet eleje)
            aimsg = "Foglald össze nekem ezeket az üzeneteket, mond a lényeget és a fontos információkat. Kezd a küldő nevével. Például valami ilyesmi módon kell válaszolnod: \"Bence azt üzeni hogy ma mégsem ér rá\". Ne paranccsal válaszolj, hanem könnyen érthető szöveggel ami összefoglalja az üzenetek tartalmát, és hogy kitől jött.\n"

            # Üzenetek összeírása egy könnyen olvasható formátumba
            for i in range(len(config.new_messages)):
                writer = config.new_messengers[i]
                message = config.new_messages[i]
                aimsg = aimsg + writer + ": " + message + "\n" # hozzáadás az AI kérelemhez

            # Új üzenetek listájának törlése
            config.new_messages = []
            config.new_messengers = []

            # Küldés az AI-nak
            return ai(aimsg)
                
    else:
        # Ha nem parancsot küldött az AI,
        # akkor csak ki kell mondatni TTS-el a választ
        return response

# Google TTS
# Ez csak az alap Google Fordítós TTS
def sgtts(text, lang="hu", volume=1):
    gtts(text, lang=lang).save("out.mp3")
    os.system("play -v " + str(volume) + " out.mp3 tempo 1.2") # Csak linux és mac!

# OpenAI TTS
#* Figyelem: Ez a TTS nagyon beleakad a számokba.
def say(text, volume=1):
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )
    response.stream_to_file("out.mp3")
    os.system("play -v " + str(volume) + " out.mp3")


# TTS Kezelő
# Ez választja ki melyik TTS nek megy az AI üzenete
def ttshandler(text, lang="hu", volume=config.volume):
    global messages

    messages.append({"role": "assistant", "content": text})
    threading.Thread(target=savetomemory).start()

    if text == "" or text == None:
        print("Szöveg nem érkezett a TTS-nek")
        return

    if config.legacy_voice:
        sgtts(text, lang, volume=volume)
    else:
        say(text, volume=volume)

# Google Szövegfelismerés 
def oldstt(playsound=True, recogntimeout=5, recmic=micid, reclang="hu-HU"):
    try:
        if playsound:
            threading.Thread(target=playsfx, args=("on", config.volume)).start()
        print("Beszélj!")
        try:
            r=sr.Recognizer()
        except Exception as e:
            print("Felismerő indítása sikertelen: " + str(e))
        
        try:
            with sr.Microphone(recmic) as source:
                try:
                    r.adjust_for_ambient_noise(source)
                except Exception as e:
                    print("Nem lehet háttérzajhoz viszonyítani: " + str(e))

                try:
                    out = r.listen(source, timeout=recogntimeout)
                except KeyboardInterrupt:
                    exit(0)
                except Exception as e:
                    out = ""
                    print("Nem kezdtél el beszélni, vagy HIBA.")
                    print(e)
        except Exception as e:
            print("sr.Microphone indítása sikertelen: " + str(e))
            out = ""

        if out:
            try:
                recogn = r.recognize_google(out, language=reclang).lower()
            except Exception as e:
                print("Hiba! errcode: '" + str(e) + "'")
                recogn = ""
            except sr.exceptions.WaitTimeoutError:
                print("Nem kezdtél el beszélni. WaitTimeoutError")
                recogn = ""
            except sr.exceptions.TranscriptionFailed:
                print("Sikertelen hangátalakítás. TranscriptionFailed")
                recogn = ""
            except sr.exceptions.UnknownValueError:
                print("Ismeretlen adat. UnknownValueError")
                recogn = ""
            except sr.exceptions.RequestError:
                print("A szolgáltatás nem elérhető")
                recogn = ""
        else: 
            recogn = ""

        print("Ezt mondtad: " + recogn)
        if playsound:
            threading.Thread(target=playsfx, args=("recognstop", config.volume)).start()
    except KeyboardInterrupt:
        return False
    except Exception as e:
        print("Error while recording: " + str(e))
        exit()

    return recogn

# Szövegfelismerés PvRecorder-rel és OpenAI-al
#* figyelem: a beszéded végén meg kell nyomnod a CTRL+C-t,
#* és még ez annyira nem működik.
def newstt():
    recorder = PvRecorder(device_index=0, frame_length=512)
    audio = []

    try:
        recorder.start()

        while True:
            frame = recorder.read()
            audio.extend(frame)
    except KeyboardInterrupt:
        recorder.stop()
        with wave.open("output.wav", 'w') as f:  # Specify the desired output file name
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
    finally:
        recorder.delete()

    audio_file= open("output.wav", "rb")
    recogn = str(client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    ).text)

# Utolsó Discord üzenet megtekintése egy csatornában
# ez a funkció sok mindenhez kell.
def get_last_discord_message(channel):
    header = {
        "authorization": config.discord_token,
        "user-agent": "Anna-AI/1.0 (https://github.com/cablesalty/Anna-AI)",
        "content-type": "application/x-www-form-urlencoded"
    }

    messagesListString = requests.get(f"https://discord.com/api/v9/channels/{channel}/messages?limit=1", headers=header).text
    messageList = json.loads(messagesListString)[0]

    content = messageList["content"]
    sender = messageList["author"]["username"]

    return content, sender


# Háttérfolyamat bejövő Discord üzenetek olvasására
# Ez szükséges az AI-nak az üzenetek olvasására és az
# értesítésekhez.
def monitor_discord():
    print("Felkészülés a Discord üzenetek olvasására (mentálisan)...")

    idlist = []
    idtoname = {}

    # Mindenkinek lekéri a telefonkönyvből az ID-ját
    for name in config.phonebook:
        nid = config.phonebook[name]
        idlist.append(nid)
        idtoname[nid] = name

    # Debug
    print(idlist)
    print(idtoname)

    # Utolsó üzenetek lista létrehozása
    last_message = {}
    for id in idlist:
        last_message[id] = ""
    print(last_message)

    # Üzenetek megtekintése
    for id in idlist:
        lastdm, lastmessenger = get_last_discord_message(id)
        if not lastdm == last_message[id]: # ha új az üzenet
            print("feldolgozás: " + id)
            last_message[id] = lastdm # hozzáadás listához

    print(last_message) # Debug

    print("Folyamatos olvasás loop elindítva")
    config.is_getting_ready = False # Kérdezésre kész!
    while True:
        # Minden felhasználó ID-jén végigloopol
        for id in idlist:
            lastdm, lastmessenger = get_last_discord_message(id) # Utolsó DM és küldő lekérése
            if lastmessenger == config.mydcusername: # Ha te küldted az utolsó üzenetet ne csináljon semmit a script
                pass
            elif not lastdm == last_message[id]: # Ha az utolsó DM nem egyezik a mostan lekért üzenettel (új üzenet)
                print("Új Discord üzenet!")
                playsfx("notification.wav")
                # Új üzenet hozzáadása a listához
                config.new_messengers.append(idtoname[id])
                config.new_messages.append(lastdm)
                last_message[id] = lastdm
                print(last_message) # Debug
            time.sleep(1)
        time.sleep(3) # Hogy ne legyen rate-limitelve a script, 3 mp-ként nézi meg hogy van e új üzenet

# Hangeffekt lejátszása
def playsfx(filename, volume=1):
    if "." in filename:
        os.system("play -v " + str(volume) + " sfx/" + filename + " >/dev/null")
    else:
        os.system("play -v " + str(volume) + " sfx/" + filename + ".mp3 >/dev/null")

# A main loop
def mainloop():
    global followupquestion
    print("Main Loop Elindítva.")
    while True:
        try:
            global messages
            # Ha a memória eléri a 40 tagot (üzenetet), akkor töröljük
            # a memóriát. Ez azért szükséges, hogy ne lépjük túl az AI
            # max_token limitjét.
            if len(messages) >= 40: 
                print("FIGYELEM: Memória elérte a 40 üzenetet. Törlés...")
                messages=config.default_messages

            print()

            # Követőkérdés: Az AI rögtön tud hallgatni következő kérdésre
            # a válasza után néhány esetben. Pl.:
            # Ha azt mondod hogy hello és az AI válaszol, akkor nem kell
            # mégegyszer azt mondanod hogy "hé anna" vagy megnyomni az
            # entert, hanem rögtön tudsz utánna beszélni
            if followupquestion:
                print("FOQ Érzékelve!")

                # Ezt a funkciót ki tudod kapcsolni.
                if allowFollowUpQuestions:
                    print("FOQ Engedélyezve, activating AI")
                    followupquestion = False
                    pass
                else: 
                    print("FOQ NINCS engedélyezve!")
                    followupquestion = False

                    # Hangaktiválás: nem csak az enter gombbal tudod aktiválni az
                    # AI-t hanem a hangoddal is!
                    if voiceactivated:
                        while True:
                            wakewordlist = ["hi anna", "hé anna", "hallgass anna", "ok anna", "hello anna", "hey anna", "héj anna"]
                            uvoicecheck = str(oldstt(playsound=False, recogntimeout=2)).strip()
                            wake_word_detected = False
                            for wakeword in wakewordlist:
                                if wakeword in uvoicecheck:
                                    wake_word_detected = True
                                    break
                            if wake_word_detected:
                                break
                            elif uvoicecheck == "kilépés":
                                print("Kilépés...")
                                exit()
                    else:
                        input("Nyomd meg az entert a beszéléshez, CTRL+C-t a megszakításhoz")

            # Hangaktiválás: nem csak az enter gombbal tudod aktiválni az
            # AI-t hanem a hangoddal is!
            elif voiceactivated:
                while True:
                    wakewordlist = ["hi anna", "hé anna", "hallgass anna", "ok anna", "hello anna", "hey anna", "héj anna"]
                    uvoicecheck = str(oldstt(playsound=False, recogntimeout=2)).strip()
                    wake_word_detected = False
                    for wakeword in wakewordlist:
                        if wakeword in uvoicecheck:
                            wake_word_detected = True
                            break
                    if wake_word_detected:
                        break
                    elif uvoicecheck == "kilépés":
                        print("Exiting...")
                        exit()

            else:
                input("Nyomd meg az entert a beszéléshez, CTRL+C-t a megszakításhoz")
        except Exception as e:
            print("Hiba hangfelismerés közben: " + str(e))
            exit()
        except KeyboardInterrupt:
            print("Interrupt.")
            exit()

        recogn = oldstt()
        if not recogn:
            continue

        print(recogn)

        # Megnézzük, hogy a hangfelismerés érzékelt e valamit
        if not recogn == "":
            try:
                # Hangbeállítások
                if recogn.startswith("hang"):
                    if "régi" in recogn:
                        config.legacy_voice = True
                        ttshandler("A hang visszaállítva a régire.")
                    elif "új" in recogn:
                        config.legacy_voice = False
                        ttshandler("A hang mostantól új.")
                    else:
                        ttshandler("Helytelen hang.")

                # Memória beállítások
                elif recogn.startswith("memória"):
                    if "visszaáll" in recogn or "tör" in recogn:
                        messages=config.default_messages
                        ttshandler("A memória törölve.")

                # AI
                else:    
                    airesp = str(ai(recogn, config.last_ai_response, config.last_user_question))

                    # Ha az üzenet __FOLLOWUP__-ra végződik
                    if airesp.endswith("__FOLLOWUP__"):
                        followupquestion = True
                        airesp = airesp.replace("__FOLLOWUP__", "")

                    ttshandler(airesp)

            except Exception as e:
                print("Hiba: " + str(e))
                exit()
        else:
            print("Nem mondtál semmit.")

# Indítás előtti funkció
if __name__ == "__main__":
    print("Indítás...")
    print("Anna-AI: cablesalty")

    print("AI Adatok betöltése...")

    # A trainerdata mappa sok adatot tartalmaz az AI-nak, ami
    # megmondja neki, hogy hogyan viselkedjen!
    for file in os.listdir("trainerdata/"):
        print("Opening " + file)
        with open("trainerdata/" + file, "r") as f:
            config.default_messages.append({"role": "system", "content": f.read()})
            f.close()

    print("AI Adatok betöltése: Kész!")


    # Általában egy gépben több mikrofon van, szóval ez lekéri a mikrofonok indexét a használatra.
    print("Mikrofonok keresése...")
    for index, name in enumerate(sr.Microphone.list_microphone_names()):
        print("Mikrofon \"{1}\" megtalálva. ID `Microphone(device_index={0})`".format(index, name))
    print("Mikrofon kiválasztva: " + str(micid))

    # Discord üzenet figyelő indítása ha van tokened
    if not config.discord_token == "":
        print("Thread indítása Discord üzenetek figyelésére...")
        threading.Thread(target=monitor_discord).start()
        print("Indítva.")
        print("Várakozás a Discord üzenet figyelőre...")
    else:
        print("HIBA: Nincs Discord token megadva!")
        print("HIBA: Folytatás Discord funkciók nélkül!")
        config.is_getting_ready = False

    # Várakozás a Discord thread befejezésére
    while config.is_getting_ready:
        time.sleep(1)

    print("Main Loop indítása...")
    mainloop()