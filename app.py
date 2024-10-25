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

st.info('Todos los casos son derivados de casos clínicos reales totalmente anonimizados y los datos del paciente estan protegidos', icon="ℹ️")
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
Paciente masculino de 52 años, casado, con secundaria completa, vive en zona urbana. Se está evaluando para ser candidato a trasplante renal. Tiene antecedentes de hipertensión arterial mal controlada, enfermedad renal crónica estadio 5 en terapia de reemplazo renal secundaria a glomerulonefritis, dislipidemia mixta, diabetes mellitus tipo 2 de 10 años de evolución y obesidad (IMC 32). Además, refiere episodios ocasionales de apnea del sueño sin tratamiento formal.

Desde hace 5 meses, el paciente ha presentado un deterioro progresivo de su función renal, con edemas en extremidades inferiores, fatiga crónica, disnea de pequeños esfuerzos y episodios de hipertensión refractaria. Recientemente, ha comenzado con prurito urémico generalizado que empeora durante la noche, lo que afecta su calidad de vida.

Ha estado hospitalizado previamente por descompensaciones hipertensivas y control insuficiente de la sobrecarga de volumen. En su último ingreso hospitalario, fue necesario iniciar diálisis peritoneal como tratamiento de urgencia.

En el examen físico actual, presenta edemas en ambos miembros inferiores con fóvea hasta rodillas, prurito generalizado sin lesiones visibles, palidez cutánea y mucosa, y signos de sobrecarga de volumen con estertores bibasales. Los laboratorios recientes muestran anemia normocítica normocrómica, aumento de creatinina y urea, hiperfosfatemia, e hiperparatiroidismo secundario. Está en tratamiento con quelantes de fosfato, antihipertensivos (incluyendo un IECA), y manejo conservador de la diálisis peritoneal.

Se encuentra en evaluación pretrasplante y pendiente de la realización de un ecocardiograma y estudios de compatibilidad inmunológica.

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


