import os
from groq import Groq
from langchain_groq import ChatGroq
import streamlit as st
from streamlit_chat import message as st_message
from langchain.schema import SystemMessage, HumanMessage, AIMessage

# Configurar la página
st.set_page_config(
    page_title="Chatbot Casos Clínicos",
    page_icon="🩺",
    layout="centered",
    initial_sidebar_state="auto",
)

st.sidebar.image("UdeA+simplificado-01.png", width=200)
st.sidebar.title("Chatbot Casos Clínicos")
st.sidebar.write("Entrega Diplomado integración TICs 2024-2") 
st.sidebar.write("Alejandro Hernández-Arango, MD, MSc")


# Verificar que la clave de API se ha cargado
api_key= st.secrets.API_KEY
# Inicializar el cliente de Groq
client = Groq(
    api_key=api_key
)

# Inicializar el modelo de chat
chat_groq = ChatGroq(model="llama-3.1-70b-versatile",api_key=api_key)

# Definir el rol del profesor y el caso clínico
professor_role = """
Eres un profesor de Medicina Interna. Vas a presentar un caso clínico a un estudiante de medicina. Comenzarás dando una introducción detallada del paciente y los síntomas principales. Tu objetivo es guiar al estudiante para que solicite los exámenes adecuados y llegue al diagnóstico de DRESS (Reacción a Fármacos con Eosinofilia y Síntomas Sistémicos). Si el estudiante se desvía, gentilmente redirígelo con preguntas y sugerencias. No reveles el diagnóstico hasta que el estudiante lo haya deducido.
"""

# Caso clínico detallado
clinical_case = """
Paciente masculino de 92 años, viudo, con primaria incompleta, vive solo en zona rural. Ingresó por presentar dolor intenso en la pierna derecha. Tiene antecedentes de hipertensión arterial, dislipidemia mixta, enfermedad venosa crónica (CEAP 6), hipoacusia bilateral grave, prediabetes, osteoporosis grave con fracturas vertebrales recientes y síndrome de caídas recurrentes.

Desde hace 15 años presenta prurito crónico, que empeoró en los últimos 7 meses, con aumento de lesiones eritematosas generalizadas en piel en forma de placas. Ha sido hospitalizado varias veces por este motivo. 

Recientemente, desarrolló fiebre, edema en extremidades inferiores y lesiones descamativas en la pierna derecha con flictenas que supuran material seroso, además de úlceras superficiales dolorosas. Decidió no usar esteroide tópico indicado y manejó el dolor con naproxeno a demanda.

En el examen físico actual, presenta prurito generalizado, lesiones descamativas en extremidades inferiores, tórax, abdomen y espalda. Tiene una úlcera en tercio distal de la pierna derecha de 12x8 cm, con bordes irregulares y supuración. Laboratorios muestran linfopenia y eosinofilia. No se han identificado signos de infección en las úlceras.

Se encuentra en espera de nueva biopsia de piel y doppler venoso de miembros inferiores. Actualmente en manejo con antihistamínicos, betametasona tópica y analgésicos.

¿Cuáles serían tus próximos pasos en el abordaje diagnóstico y terapéutico de este paciente?
"""

# Inicializar el historial en la sesión
if 'messages' not in st.session_state:
    # Configurar mensajes iniciales
    st.session_state.messages = [SystemMessage(content=professor_role)]
    st.session_state.messages.append(AIMessage(content="Hola, hoy discutiremos un caso clínico."))
    st.session_state.messages.append(AIMessage(content=clinical_case))
    # Historial para mostrar en la interfaz
    st.session_state.history = [
        {"role": "Profesor", "content": "Hola, hoy discutiremos un caso clínico."},
        {"role": "Profesor", "content": clinical_case},
    ]

# Función para manejar la interacción con el chatbot
def chat_with_student(student_input):
    # Agregar la entrada del estudiante al historial
    st.session_state.messages.append(HumanMessage(content=student_input))
    st.session_state.history.append({"role": "Estudiante", "content": student_input})
    # Obtener la respuesta del modelo
    response = chat_groq.invoke(st.session_state.messages)
    # Agregar la respuesta del profesor al historial
    st.session_state.messages.append(AIMessage(content=response.content))
    st.session_state.history.append({"role": "Profesor", "content": response.content})

# Interfaz de Streamlit
def main():


    # Mostrar la conversación
    for msg in st.session_state.history:
        if msg["role"] == "Estudiante":
            st_message(msg["content"], is_user=True)
        else:
            st_message(msg["content"])

    # Formulario de entrada del estudiante
    with st.form(key='chat_form', clear_on_submit=True):
        student_input = st.text_input("Estudiante:", placeholder="Escribe tu respuesta aquí...")
        submit_button = st.form_submit_button(label='Enviar')

    if submit_button:
        if student_input:
            chat_with_student(student_input)
            st.rerun()  # Recargar para mostrar la nueva conversación
        else:
            st.warning("Por favor, escribe una respuesta antes de enviar.")

if __name__ == "__main__":
    main()


