import streamlit as st
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
import requests
from streamlit_lottie import st_lottie
from PIL import Image 
import numpy as np
import os
import openai

from dotenv import load_dotenv
import os
import openai

def thematique (x):
    def change_e(text):
        def replace_letter(word, index, new_letter):
            # Convert the word to a list of characters
            letters = list(word)
            letters[index] = new_letter
            new_word = ''.join(letters)
            return new_word

        for i in range(len(text)):
            if text[i]=='1':
                text=replace_letter(text,i,'e')
            if text[i]=="'":
                text=replace_letter(text,i,' ')
        return text
    
    def extract_thematique(x):
        types=['Renseignement juridique', 'Comptabilité', 'Banque','Droit social', 'Domiciliation']
        for type in types:
            if type.upper() in x.upper():
                
                return type
        
        return 'none'

    delimiter = "####"
    system_message = f"""
    Tu es un juriste competant ayant pour mission de classifier des messages clients .Étant donné le message d'un client d'une entreprise juridique,tu dois sélectionnez la categorie 
    la mieux adaptée à l'entrée. 
    le message du client sera delimité par {delimiter} 

    suit les etapes suivantes precisement pour donner la bonne reponse

    etape 1:{delimiter} tu dois comprendre le message ,le reformuler en le resumant avec conservation de contexte


    etape 2:{delimiter} tu dois classifier le message en une des thematiques suivantes,voici une description de chaque categories

    Renseignement juridique : Cette catégorie concerne les demandes d'informations juridiques. 
    Elle englobe des questions relatives aux lois, aux réglementations, aux droits et aux obligations légales.
     Les messages de cette catégorie peuvent être liés à des problèmes juridiques personnels,
     à des conseils pour la création d'une entreprise, à des contrats, à des litiges, etc.
    voici des examples ou tu dois choisir Renseignement juridique

    message=Je suis en train de créer ma holding, et je voudrais que la SASU que je possède déjà soit 100% détenue par la holding.Mais dans le formulaire de création de la holding, je n'ai pas vu de point me permettant de saisir cette information. Comment faire?
    reponse=Renseignement juridique{delimiter}Je suis en train de créer ma holding, et je voudrais que la SASU que je possède déjà soit 100% détenue par la holding.Mais dans le formulaire de création de la holding, je n'ai pas vu de point me permettant de saisir cette information. Comment faire?{delimiter}

    message=Bonjour, dans le cadre de l'ouverture de ma SASU, quels sont le domaine d'activité et les activités à sélectionner ? Je suis consultante en marketing et communication. Je vais également proposer des formations et des audit flash via mon site e commerce -> possibilité de commander un service et de l'acheter en ligne.
    reponse=Renseignement juridique{delimiter}Bonjour, dans le cadre de l'ouverture de ma SASU, quels sont le domaine d'activité et les activités à sélectionner ? Je suis consultante en marketing et communication. Je vais également proposer des formations et des audit flash via mon site e commerce -> possibilité de commander un service et de l'acheter en ligne.{delimiter}

    message=Bonjour, j'aurai besoin d'un Kbis à jour. Pouvez vouez m'aider à m'en procurer un ? Merci
    reponse=Renseignement juridique{delimiter}Bonjour, j'aurai besoin d'un Kbis à jour. Pouvez vouez m'aider à m'en procurer un ? Merci{delimiter}

    message= mutuelle prendre en tant que gérant non associé de la EURL, est ce assimilé salarié ou travailleur non salariés car sur certains sites, il est mentionné que gérant non associé est (assimilé salarié), merci d'avance
    reponse=Renseignement juridique{delimiter}mutuelle prendre en tant que gérant non associé de la EURL, est ce assimilé salarié ou travailleur non salariés car sur certains sites, il est mentionné que gérant non associé est (assimilé salarié), merci d'avance{delimiter}

    message=quelles démarches à réaliser auprès de l'URSSAF
    reponse=Renseignement juridique{delimiter}quelles démarches à réaliser auprès de l'URSSAF{delimiter}


    Banque :  Cette catégorie concerne les questions relatives aux services bancaires.
    Les messages de cette catégorie peuvent porter sur des demandes d'ouverture de compte, de prêts, de conseils en matière d'investissement,
    de gestion des finances personnelles, de transactions bancaires, de cartes de crédit, etc. Les requêtes sur les politiques bancaires,
    les taux d'intérêt, les garanties et les produits financiers peuvent également être classées dans cette catégorie.
    voici des examples ou tu dois choisir Banque

    message=Je veux changer de banque pour mon compte pro et déposer le capital social et les statuts d l'entreprise dans une autre banque
    reponse=Banque{delimiter}Je veux changer de banque pour mon compte pro et déposer le capital social et les statuts d l'entreprise dans une autre banque{delimiter}


    Domiciliation : Cette catégorie concerne les demandes liées à l'établissement ou à la gestion d'une adresse commerciale ou résidentielle. 
    Les messages de cette catégorie peuvent porter sur des sujets tels que la location de bureaux, les services de réexpédition de courrier, 
    la gestion des colis, les formalités administratives pour changer d'adresse, les services de conciergerie, etc.
    voici des examples ou tu dois choisir Domiciliation
    message= Bonjour, je souhaite changer le siège sociale de ma SARL. Actuellement domicilié dans le 92 à Sèvres, je compte déménager dans mon futur local. J'ai signé une promesse de vente sur ce local et j'ai une autorisation de domiciliation du propriétaire (qui détient le local en SCI). Je souhaite savoir cela est possible avant que je ne sois définitivement propriétaire ou si je dois attente d'être propriétaire?
    reponse=Domiciliation{delimiter}Bonjour, je souhaite changer le siège sociale de ma SARL. Actuellement domicilié dans le 92 à Sèvres, je compte déménager dans mon futur local. J'ai signé une promesse de vente sur ce local et j'ai une autorisation de domiciliation du propriétaire (qui détient le local en SCI). Je souhaite savoir cela est possible avant que je ne sois définitivement propriétaire ou si je dois attente d'être propriétaire?{delimiter}

    message=Pouvez vous me donner une estimation de ce que je gagne en faisant domicilier ma SASU à Paris plutôt qu'à mon domicile (Châtenay-Malabry 92290) ? Je fais du conseil en informatique, chiffre d'affaire autour de 150K€ par an.
    reponse=Domiciliation{delimiter}Pouvez vous me donner une estimation de ce que je gagne en faisant domicilier ma SASU à Paris plutôt qu'à mon domicile (Châtenay-Malabry 92290) ? Je fais du conseil en informatique, chiffre d'affaire autour de 150K€ par an.{delimiter}

    Comptabilité : Cette catégorie concerne les demandes liées à la comptabilité et à la gestion financière. 
    Les messages de cette catégorie peuvent inclure des questions sur la tenue de livres, la déclaration fiscale, 
    les normes comptables, les conseils en matière de gestion financière, les rapports financiers, les audits, etc. 
    Les requêtes sur les logiciels de comptabilité et les outils de gestion financière peuvent également être classées dans cette catégorie.
    voici des examples ou tu dois choisir Comptabilité
    message=Bonjour, pour une SARL , l'associé minoritaire doit il obligatoirement être salarié dans les premiers mois de la création d'entreprise ?
    reponse= Comptabilité {delimiter}Bonjour, pour une SARL , l'associé minoritaire doit il obligatoirement être salarié dans les premiers mois de la création d'entreprise ?{delimiter}

    message=SCI à l'IS assujettie ou non à la TVA ?
    reponse=Comptabilité{delimiter}SCI à l'IS assujettie ou non à la TVA ?{delimiter}



    RAPPEL : la reponse DOIT être l'un des noms de consigne candidats spécifiés ci-dessus suivie de {delimiter} et le message original du client
    voici quelques exemples de message et de la reponse demandée:

    
    suit les etapes suivantes pour repondre
    etape 1:{delimiter} 
    etape 2:{delimiter} 
    

    """
    user_message = change_e(x)	
    messages =  [  
{'role':'system', 
 'content': system_message},    
{'role':'user', 
 'content': f"{delimiter}{user_message}{delimiter}"},  
] 
    response = get_completion_from_messages(messages)
    
    return extract_thematique(response)

def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo-0613",
                                 temperature=0,
                                 max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]
from dotenv import load_dotenv
import os
import openai
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_key = openai.api_key.replace("<", "").replace(">", "")



image_folder="./images"
st.set_page_config(page_title='Classifier UI',page_icon=":tada",layout="wide")
def load_lottieur1(url):
    r=requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()

def local_css(file_name):
   with open(file_name) as f:
       st.markdown(f'<style>{f.read()}</style>',unsafe_allow_html=True) 

lottie_coding=load_lottieur1("https://assets1.lottiefiles.com/packages/lf20_3rwasyjy.json")
logo=Image.open('./images/logo.png')
st.image(logo)

st.title('Hi ,  im Gouga :wave:')
st.subheader('from Legal Place')

with st.sidebar:

    name = st.text_input('name')
    last_name = st.text_input('last name')

question = st.text_input("tell me how can i help", placeholder="")

if question:
        with st.spinner("waiting"):
            st.info(thematique(question))
    

        
