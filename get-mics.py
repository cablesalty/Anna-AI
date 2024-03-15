# get-mics.py
# Ez a fájl futtatáskor listázza az összes csatlakoztatott
# mikrofon nevét és ID-ját.

import speech_recognition as sr
for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Mikrofon \"{1}\" megtalálva. ID `Microphone(device_index={0})`".format(index, name))