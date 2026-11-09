import streamlit as st
from google import genai
from google.genai import errors

# Configuration de la page
st.set_page_config(page_title="Diagnostic des Talents et Structuration d'Équipe", layout="wide")

# Connexion à l'API Google (récupération de la clé depuis Streamlit Secrets)
api_key = st.secrets.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# Données des menus déroulants
MBTI_TYPES = [
    "ISTJ - Logisticien", "ISFJ - Défenseur", "INFJ - Avocat", "INTJ - Architecte",
    "ISTP - Virtuose", "ISFP - Aventurier", "INFP - Médiateur", "INTP - Logicien",
    "ESTP - Entrepreneur", "ESFP - Amuseur", "ENFP - Inspirateur", "ENTP - Innovateur",
    "ESTJ - Directeur", "ESFJ - Consul", "ENFJ - Protagoniste", "ENTJ - Commandant"
]

INTELLIGENCES = [
    "Linguistique (mots, écriture, expression orale)",
    "Logico-mathématique (chiffres, logique, rigueur d'analyse)",
    "Spatiale / Visuelle (formes, schémas, maquettes, design)",
    "Kinesthésique (action, manipulation physique, fabrication)",
    "Interpersonnelle (relations, écoute, empathie, leadership)",
    "Intrapersonnelle (introspection, recul, stratégie personnelle)",
    "Naturaliste (sensibilité aux systèmes, à l'environnement et au vivant)",
    "Musicale / Rythmique (rythme, sensibilité aux ambiances et structures)"
]

VERBES = [
    "Imaginer, dessiner, rêver, inventer (mille idées et créativité)",
    "Fabriquer, assembler, concevoir (fabriquer les idées des autres)",
    "Diriger, manager (rassembler et organiser le travail d'équipe)",
    "Gérer, chiffrer (calculer, régler les problèmes et les flux)",
    "Prévoir, ranger (talent pour structurer et planifier)",
    "Représenter, fédérer, animer (trouver les arguments pour convaincre)",
    "Communiquer, échanger (discuter, animer et présenter)",
    "Contrôler, vérifier (s'assurer du bon fonctionnement et fiabiliser)"
]

TYPES_EVENEMENT = [
    "Hackathon (Création d'un projet, d'une solution ou start-up)",
    "Convention (Enquête, interviews, élaboration d'une vision, création d'un poster et présentation orale)"
]

st.title("Diagnostic des Talents & Structuration d'Équipe")
st.markdown("Renseignez le type d'événement et les profils de votre équipe pour révéler vos complémentarités et attribuer les responsabilités du projet.")

# Choix du type d'événement
type_evenement = st.selectbox("Dans quel cadre se réunit cette équipe ?", TYPES_EVENEMENT)

st.markdown("---")

# Curseur de 1 à 10 membres
nb_membres = st.slider("Nombre de participants dans l'équipe :", min_value=1, max_value=10, value=4)

membres_data = []
colonnes = st.columns(2)

# Génération des fiches de saisie
for i in range(nb_membres):
    col = colonnes[i % 2]
    with col:
        st.subheader(f"Membre {i + 1}")
        nom = st.text_input(f"Prénom :", key=f"nom_{i}", placeholder=f"Ex: Participant {i+1}")
        mbti = st.selectbox(f"Profil MBTI :", MBTI_TYPES, key=f"mbti_{i}")
        intel_1 = st.selectbox(f"Intelligence dominante n°1 :", INTELLIGENCES, key=f"intel1_{i}")
        intel_2 = st.selectbox(f"Intelligence dominante n°2 :", INTELLIGENCES, key=f"intel2_{i}", index=1)
        verbe_1 = st.selectbox(f"Verbe de talent n°1 :", VERBES, key=f"verbe1_{i}")
        verbe_2 = st.selectbox(f"Verbe de talent n°2 :", VERBES, key=f"verbe2_{i}", index=1)
        valeurs = st.text_input(f"3 à 4 valeurs clés :", key=f"val_{i}", placeholder="Ex: Rigueur, Écologie, Écoute")
        
        membres_data.append({
            "prenom": nom if nom else f"Membre {i+1}",
            "mbti": mbti,
            "intel_1": intel_1,
            "intel_2": intel_2,
            "verbe_1": verbe_1,
            "verbe_2": verbe_2,
            "valeurs": valeurs
        })

system_prompt = f"""
Tu es un expert en dynamique d'équipe et accompagnement de jeunes talents (éco-délégués).
Le contexte du travail de cette équipe (1 à 10 personnes) est le suivant : {type_evenement}.
Analyse l'équipe selon les données fournies : MBTI, 2 Intelligences de Gardner, 2 Verbes de talents et Valeurs.

Structure ta réponse EXACTEMENT ainsi :

### 1. Cartographie de l'équipe
- **Les Forces :** Décris la dynamique collective, l'énergie dominante et la créativité du groupe adaptées au type d'événement.
- **Points de Vigilance :** Ce qui manque à l'équipe et ce qui risque de les bloquer.

### 2. Attribution des Postes & Missions
Le format des rôles dépend STRICTEMENT du contexte :

- SI le contexte est "Hackathon (Création d'un projet, d'une solution ou start-up)", attribue à CHAQUE membre un rôle exécutif officiel de start-up (ex: CEO, CMO, CTO, CDO, CFO, COO...).

- SI le contexte est "Convention", NE DONNE PAS de rôles d'entreprise. Attribue des rôles spécifiques à une mission d'enquête citoyenne (recherche, interviews de terrain, formulation de la vision, conception du poster et pitch oral devant un jury). 
Exemples de rôles possibles : Coordinateur des Interviews, Analyste/Chercheur (Sources & Données), Concepteur Visuel (Poster), Porte-Parole (Pitch oral), ou Stratège de la Vision. IL N'Y A AUCUN REPORTAGE VIDÉO À PRODUIRE.

Formule le résultat sous cette forme stricte :
**[Prénom] : [Titre du rôle adapté au contexte] / [Mission]**
- **Ta mission concrète :** Explique son rôle opérationnel direct en justifiant par ses talents (MBTI, intelligences, verbes).
- **Attention à la fatigue :** Indique les tâches ou contextes qui vont l'épuiser (sa zone de frustration) et qu'il/elle doit éviter.

Sois ultra-professionnel, bienveillant, valorisant et inspirant.
"""

if st.button("Révéler les rôles de l'équipe", type="primary"):
    with st.spinner("Un instant, j'analyse vos talents..."):
        user_content = f"L'équipe est composée de {nb_membres} personne(s) :\n"
        for m in membres_data:
            user_content += (
                f"- {m['prenom']} | MBTI: {m['mbti']} | "
                f"Intelligences: 1. {m['intel_1']} / 2. {m['intel_2']} | "
                f"Verbes: 1. {m['verbe_1']} / 2. {m['verbe_2']} | "
                f"Valeurs: {m['valeurs']}\n"
            )
        
        try:
            # Appel direct au modèle de production
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[system_prompt, user_content]
            )
            st.success("Diagnostic d'équipe prêt !")
            st.markdown(response.text)
        except errors.APIError as e:
            st.error(f"Une erreur technique est survenue : {e}")
