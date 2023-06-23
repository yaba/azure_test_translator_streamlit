import streamlit as st
import os

from azure.ai.translation.text import TextTranslationClient, TranslatorCredential
from azure.ai.translation.text.models import InputTextItem
from azure.core.exceptions import HttpResponseError

key = os.environ["KEY"] 
endpoint = "https://api.cognitive.microsofttranslator.com/"
region = "eastus"

credential = TranslatorCredential(key, region)
text_translator = TextTranslationClient(endpoint=endpoint, credential=credential)

language_map_name = {}
language_map_code = {}

try:
    scope = "translation"
    response = response = text_translator.get_languages(scope=scope)
    for key in response.translation.keys():
        language_map_name[response.translation[key].name] = key
        language_map_code[key] = response.translation[key].name

except HttpResponseError as exception:
    print(f"Error Code: {exception.error.code}")
    print(f"Message: {exception.error.message}")

def translateTextAutodetect(output_language, txt):
    try:
        output_language = language_map_name[output_language]
        input_text_elements = [ InputTextItem(text = txt) ]

        response = text_translator.translate(content = input_text_elements, to = [output_language])
        translation = response[0] if response else None

        if translation:
            detected_language = translation.detected_language
            if detected_language:
                print(f"Detected languages of the input text: {detected_language.language} with score: {detected_language.score}.")
            for translated_text in translation.translations:
                print(f"Text was translated to: '{translated_text.to}' and the result is: '{translated_text.text}'.")
            message = translated_text.text
            detected_language = detected_language.language

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
        message = exception.error.message
        detected_language = None

    return message, detected_language

def translateText(input_language, output_language, txt):
    try:
        input_language = language_map_name[input_language]
        output_language = language_map_name[output_language]
        input_text = [ InputTextItem(text = txt) ]

        response = text_translator.translate(content = input_text, to = [output_language], from_parameter = input_language)
        translation = response[0] if response else None

        if translation:
            message = ""
            for translated_text in translation.translations:
                message = message + translated_text.text            

    except HttpResponseError as exception:
        print(f"Error Code: {exception.error.code}")
        print(f"Message: {exception.error.message}")
        message = exception.error.message

    return message

st.set_page_config(layout="wide")

input_option_autodetect = [value['name'] for value in response.translation.values()]
input_option_autodetect.insert(0, "AUTODETECT")
input_option = st.selectbox(
    'Input language?',
    #([value['name'] for value in response.translation.values()]))
    input_option_autodetect)

output_option = st.selectbox(
    'Output language?',
    ([value['name'] for value in response.translation.values()]))

input_text = st.text_area('Text to translate')

if st.button('Translate'):
    if input_option == 'AUTODETECT':
        output_text, detected_language = translateTextAutodetect(output_option, input_text)
        st.write("Detected language: " + language_map_code[detected_language])
        st.write("Translated text:\n\n" + output_text)
    else:
        output_text = translateText(input_option, output_option, input_text)
        st.write(output_text)
