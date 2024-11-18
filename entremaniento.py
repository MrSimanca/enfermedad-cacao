import streamlit as st
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
import numpy as np
import logging
import bcrypt
from io import BytesIO
import streamlit.components.v1 as components

# Configurar logging
logging.basicConfig(level=logging.INFO, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")

# Funciones para manejo de usuarios
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(stored_hash, password):
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# Diccionario de usuarios
USER_CREDENTIALS = {
    "yeimer": hash_password("password123"),
    "user1": hash_password("securepass")
}

# Estilos CSS
st.markdown(
    """
    <style>
    /* General */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #fafafa;
        color: #333;
    }
    
    /* Barra lateral */
    .sidebar .sidebar-content {
        background-color: #f4f6f8; 
    }
    
    /* Estilos del título */
    .stApp h1 {
        color: #1e3d58;
        font-size: 36px;
        font-weight: bold;
    }
    
    .stApp h2 {
        color: #2d3748;
        font-size: 28px;
        font-weight: 600;
    }

    /* Estilo de botones */
    .stButton > button {
        background-color: #4CAF50; 
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
        transition: background-color 0.3s;
    }

    .stButton > button:hover {
        background-color: #45a049;
    }

    /* Estilo de campos de texto */
    .stTextInput > div > div > input {
        border: 1px solid #ccc;
        padding: 10px;
        border-radius: 8px;
        font-size: 16px;
    }

    .stTextInput > div > div > input:focus {
        outline: none;
        border: 2px solid #4CAF50;
    }

    /* Imágenes */
    .image-container img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }

    /* Estilo de la barra lateral */
    .sidebar .sidebar-content {
        padding-top: 20px;
    }

    /* Estilo responsive */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
        }

        .stTextInput > div > div > input {
            width: 100%;
        }

        .stApp h1 {
            font-size: 28px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Función de login
def login():
    st.sidebar.title("Inicio de Sesión")
    username = st.sidebar.text_input("Usuario", key="username_input")
    password = st.sidebar.text_input("Contraseña", type="password" if not st.sidebar.checkbox("Mostrar contraseña") else "default", key="password_input")

    login_button = st.sidebar.button("Iniciar sesión", disabled=not username or not password)

    if login_button:
        if username in USER_CREDENTIALS and check_password(USER_CREDENTIALS[username], password):
            st.session_state["authenticated"] = True
            st.sidebar.success("Inicio de sesión exitoso")
        else:
            st.sidebar.error("Usuario o contraseña incorrectos")

# Inicializar el estado de sesión
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login()
else:
    # Cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.update({"authenticated": False})
        st.sidebar.success("Sesión cerrada con éxito.")

    # Contenido de la aplicación después del inicio de sesión
    st.title("DETECCIÓN DE MONILIASIS EN PLANTACIONES DE CACAO 🌱")
    st.markdown(
        """
        Bienvenido a la herramienta de detección de enfermedades en cacao. 
        Sube una imagen para identificar si la planta presenta Monilia u otras condiciones.
        """
    )

    # Cargar el modelo y las etiquetas solo una vez
    if 'model' not in st.session_state:
        st.session_state.model = load_model("keras_Model.h5", compile=False)
        st.session_state.class_names = open("labels.txt", "r").readlines()

    model = st.session_state.model
    class_names = st.session_state.class_names

    # Diccionario de recomendaciones
    recommendations = {
        "Monilia": """
        **Recomendaciones para manejar la Monilia:**
        - 🌿 **Eliminación de frutos infectados**: Retira y destruye los frutos afectados.
        - 🌞 **Ventilación y sombra**: Mantén la plantación bien aireada.
        - 💧 **Control químico y biológico**: Usa fungicidas y productos biológicos como Trichoderma spp.
        - ✂️ **Poda**: Realiza podas para mejorar la circulación de aire.
        """,
        "Sana": """
        **Recomendaciones para plantas sanas:**
        - Mantén buenas prácticas de cultivo.
        - Monitorea regularmente para prevenir problemas futuros.
        """
    }

    # Agregar Three.js para mostrar una escena 3D de una mazorca de cacao
    threejs_code = """
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Three.js Mazorca de Cacao</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
          body {
            margin: 0;
            overflow: hidden;
          }
          canvas {
            display: block;
          }
        </style>
      </head>
      <body>
        <script>
          var scene = new THREE.Scene();
          var camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
          var renderer = new THREE.WebGLRenderer();
          renderer.setSize(window.innerWidth, window.innerHeight);
          document.body.appendChild(renderer.domElement);

          // Creación de una geometría de ejemplo (cubo como la mazorca)
          var geometry = new THREE.CylinderGeometry(2, 2, 6, 32);
          var material = new THREE.MeshBasicMaterial({ color: 0x8b4513 });
          var cocoaPod = new THREE.Mesh(geometry, material);
          scene.add(cocoaPod);

          // Luz
          var light = new THREE.PointLight(0xffffff, 1, 100);
          light.position.set(10, 10, 10);
          scene.add(light);

          camera.position.z = 10;

          // Animación
          function animate() {
            requestAnimationFrame(animate);

            // Rotar la mazorca
            cocoaPod.rotation.x += 0.01;
            cocoaPod.rotation.y += 0.01;

            renderer.render(scene, camera);
          }

          animate();

          window.addEventListener("resize", () => {
            renderer.setSize(window.innerWidth, window.innerHeight);
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
          });
        </script>
      </body>
    </html>
    """

    # Mostrar la escena de Three.js en Streamlit
    components.html(threejs_code, height=600)

    # Subir imagen
    st.sidebar.subheader("Sube tu imagen:")
    uploaded_image = st.sidebar.file_uploader("Selecciona una imagen", type=["jpg", "png", "jpeg"])

    if uploaded_image is not None:
        # Procesar la imagen cargada
        image = Image.open(uploaded_image).convert("RGB")
        image.thumbnail((300, 300))  # Mantener relación de aspecto original
        st.image(image, caption="Imagen cargada", use_container_width=True)

        # Preparar la imagen para el modelo
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array

        # Spinner de predicción
        with st.spinner("Realizando predicción..."):
            try:
                prediction = model.predict(data)
            except Exception as e:
                logging.error(f"Error durante la predicción: {e}")
                st.error("Hubo un error al realizar la predicción. Intenta de nuevo más tarde.")
                st.stop()  # Detener la ejecución si ocurre un error

        # Obtener la clase con mayor probabilidad
        index = np.argmax(prediction)
        class_name = class_names[index].strip()
        confidence_score = prediction[0][index]

        # Mostrar el resultado
        st.subheader(f"Predicción: {class_name}")
        st.write(f"Probabilidad: {confidence_score * 100:.0f}%")

        # Mostrar recomendaciones
        st.write(recommendations.get(class_name, "No se tienen recomendaciones para esta condición."))
