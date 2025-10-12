import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

import os

# Configuración
#tamaño de cada carta
ANCHO_BOTON = 80
ALTO_BOTON = 80
FILAS, COLUMNAS = 6, 6 #cartas en el tablero
TOTAL_PAREJAS = (FILAS * COLUMNAS) // 2 #formar parejas

imagenes = [
    "1.jpg", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png",
    "8.png", "9.png", "10.png", "11.png", "12.png", "13.png", "14.png",
    "16.png", "17.png", "teus.png", "15.jpg"
]

# -------------------------------
def iniciar_juego(dificultad):
    juego = tk.Tk()
    juego.title(f"Memoria - {dificultad}")
    #juego.configure(bg="#222222")

    frame = tk.Frame(juego, bg="#333333", padx=50, pady=50) #fondo y tamaño de la cuadrícula de cartas
    frame.pack(expand=True)

    tiempo_dificultad = {"Fácil": 5000, "Medio": 4000, "Difícil": 3000}
    tiempo_memoria = tiempo_dificultad[dificultad]

    # Carga imágenes y crea parejas
    parejas = []
    nombres = []
    bloqueo = [False]

    for i in imagenes:
        
        #img = Image.open(i).resize((ANCHO_BOTON, ALTO_BOTON)) #abre la imagen y redimensiona

        BASE_DIR = os.path.dirname(__file__)
        img = Image.open(os.path.join(BASE_DIR, i)).resize((ANCHO_BOTON, ALTO_BOTON))
        img_tk1 = ImageTk.PhotoImage(img) #convierte la imagen en un label o botón 
        img_tk2 = ImageTk.PhotoImage(img)  # copia para que pueda aparecer dos veces
        parejas.append(img_tk1) #agrega a la lista la imagen ya convertida en label
        parejas.append(img_tk2) ##agrega a la lista la copia de imagen ya convertida en label
        nombres.append(i)
        nombres.append(i) #se agregan los nombres de las imagenes para luego ser comparadas

    # Mezclar
    temp = list(zip(parejas, nombres)) #zip junta los elementos de sus parámetros en pares, para que no se pierda la relación nombre-imagen
    random.shuffle(temp) #mezcla los elementos de la lista de manera aleatoria
    parejas, nombres = zip(*temp) #para trabajar nuevamente con dos listas paralelas, como las que necesitás para colocar imágenes y nombres en la matriz

    # Imagen de fondo

    #fondo = Image.open("fondo.png").resize((ANCHO_BOTON, ALTO_BOTON)) #imagen de fondo al ser volteada la carta
    
    fondo = Image.open(os.path.join(BASE_DIR, "fondo.png")).resize((ANCHO_BOTON, ALTO_BOTON))

    fondo_tk = ImageTk.PhotoImage(fondo) #convierte la imagen en un label o botón 

    primer_click = [None]
    #Guarda la posición del primer cuadrito que el jugador selecciona.
    #Se usa una lista con un elemento ([None]) para que pueda modificarse dentro de funciones internas sin usar global.
    #Inicialmente es None porque no se ha hecho ningún clic aún.
    #Por ejemplo: después de hacer clic en la fila 0, columna 2, se verá: primer_click[0] = (0, 2)
    segundo_click = [None]
    puntaje = [0]
    intentos = [0] 
    encontradas = [0]

    # -------------------------------
    # Crear matriz 
    labels = [] #matriz que guardará todos los Labels del tablero
    idx = 0 #variable para recorrer los labels 
    for i in range(FILAS):
        fila = []
        for j in range(COLUMNAS):
            cell_frame = tk.Frame(frame, width=ANCHO_BOTON, height=ALTO_BOTON, bg="#444444", bd=2, relief="raised")
            #bg, bordes de cuadrícula
            #bd ancho del borde
            #relief: "flat" → sin relieve
                    #"sunken" → hundido
                    #"groove" → borde con surco
                    #"ridge" → borde con relieve en cresta 
            cell_frame.grid_propagate(False) #se desactiva el ajuste automático de tamaño
            cell_frame.grid(row=i, column=j, padx=5, pady=5) #organiza los widgets en filas y columnas, asigna el espacio entre cartas

            lbl = tk.Label(cell_frame, bg="#444444", image=parejas[idx]) #muestra la imagen de la carta, color del marco de foto
            #image=parejas[idx]: que imagen debe mostrar segun el click
            lbl.pack(expand=True, fill="both") #expandir para ocupar todo el espacio disponible del frame y "both"para hacerlo vertical y horizontalmente
            lbl.imagen_real = parejas[idx] #guardamos la imagen original de la carta en el Label para luego cambiarla temporalmente por el fondo
            lbl.nombre_imagen = nombres[idx] #Guardamos el nombre del archivo de la imagen para comparar dos cartas y ver si forman pareja
            lbl.revelado = True  # inicialmente visibles
            fila.append(lbl)
            idx += 1
        labels.append(fila)

    # -------------------------------
    # Voltear todas las imágenes a fondo.png después del tiempo
    def voltear_todas():
        if not juego.winfo_exists(): #verifica si la ventana del juego todavía existe
            return
        for i in range(FILAS):
            for j in range(COLUMNAS):
                lbl = labels[i][j] #selecciona la imagen
                lbl.config(image=fondo_tk) #la cambia al fondo
                lbl.revelado = False #oculta la carta

    juego.after(tiempo_memoria, voltear_todas) #luego de tiempo_memoria, voltea las cartas

    # Temporizador 
    tiempos_limite = {"Fácil": 50, "Medio": 40, "Difícil": 30}
    tiempo_restante = [tiempos_limite[dificultad]]

    # Contenedor del temporizador (barra superior)
    frame_tiempo = tk.Frame(juego, bg="#222222")
    frame_tiempo.pack(fill="x", pady=(10, 0))

    # Texto del temporizador
    label_tiempo = tk.Label(
        frame_tiempo,
        text=f"⏳ Tiempo restante: {tiempo_restante[0]} s",
        font=("Consolas", 18, "bold"),
        fg="#00FF00",  # verde al inicio
        bg="#222222"
    )
    label_tiempo.pack(pady=5)

    # Función de actualización
    def actualizar_tiempo():
        if not juego.winfo_exists():
            return
        if tiempo_restante[0] > 0:
            tiempo_restante[0] -= 1

            # Cambia el color según el tiempo restante
            if tiempo_restante[0] > 20:
                color = "#00FF00" 
            elif tiempo_restante[0] > 10:
                color = "#FFD700"
            else:
                color = "#FF3333"

            label_tiempo.config(
                text=f"⏳ Tiempo restante: {tiempo_restante[0]} s",
                fg=color
            )

            juego.after(1000, actualizar_tiempo)
        else:
            # Cuando se acaba el tiempo, termina el juego
            messagebox.showinfo("Tiempo agotado", "¡Se acabó el tiempo!")
            finalizar_juego()

    # Iniciar el contador justo después de voltear las cartas
    def iniciar_temporizador():
        actualizar_tiempo()

    juego.after(tiempo_memoria, iniciar_temporizador)

    # -------------------------------
    # Manejo de clicks
    def check_click(i, j):
        if not juego.winfo_exists():#verifica si la ventana del juego todavía existe
            return
        if bloqueo[0]: #Evita que se abra una nueva carta mientras se está comparando las otras dos
            return
        lbl = labels[i][j]
        if lbl.revelado:
            return

        lbl.config(image=lbl.imagen_real) #voltea la carta
        lbl.revelado = True

        if not primer_click[0]: #verifica si todavía no hay una carta seleccionada como primera.
            primer_click[0] = (i, j) #Si no hay primer clic, guarda las coordenadas de la carta que se acaba de clicar
        else: #Si ya hay un primer_click, entonces esta carta es la segunda que el jugador selecciona.
            segundo_click[0] = (i, j)
            bloqueo[0] = True #Bloquea al jugador de seleccionar más cartas mientras se comparan
            juego.after(500, verificar_pareja) #Espera 500 ms (medio segundo) y luego llama a la función verificar_pareja.

    def verificar_pareja():
        if not juego.winfo_exists():
            return
        if primer_click[0] is None or segundo_click[0] is None: #comprueba si falta seleccionar una carta
            return

        i1, j1 = primer_click[0] #separa las coordenadas
        i2, j2 = segundo_click[0]

        intentos[0] += 1

        # Comparar por nombre de archivo
        if labels[i1][j1].nombre_imagen == labels[i2][j2].nombre_imagen:
            encontradas[0] +=1
            #Solo cuenta los puntos de los primeros 18 intentos:
            if intentos [0] <= 18:
                puntaje[0] += 1
            
        else:
            labels[i1][j1].config(image=fondo_tk) #si las cartas no coinciden, cambia la primera carta de nuevo a la imagen de fondo,
            labels[i2][j2].config(image=fondo_tk)
            labels[i1][j1].revelado = False
            labels[i2][j2].revelado = False

        primer_click[0] = None
        segundo_click[0] = None
        bloqueo[0] = False

        if encontradas[0] == TOTAL_PAREJAS:
            bloqueo[0] = True
            juego.after(300, finalizar_juego)

    # -------------------------------
    def finalizar_juego():
        if not juego.winfo_exists():
            return
        if puntaje[0] < 13:
            msg = "Suerte para la próxima"
        elif 13 <= puntaje[0] <= 16:
            msg = "Pasaste por poco"
        else:
            msg = "Sobresaliente"

        juego.attributes("-disabled", True)

        final = tk.Toplevel()
        final.title("Fin del juego")
        final.geometry("400x400")
        final.configure(bg = "#222222")

        final.transient(juego) #Para asegurarse de que la ventana se genere sobre el juego previo
        final.grab_set() #Para dirigir todas las acciones hacia esta ventana

        tk.Label(final, text = "Juego Terminado!", font=("Arial", 24, "bold"), fg="#FF7518", bg="#222222").pack(pady = 20)
        tk.Label(final, text = f"Puntaje: {puntaje[0]}", font = ("Arial", 16), fg = "white", bg = "#222222").pack(pady = 5)
        tk.Label(final, text = f"Intentos: {intentos[0]}",font = ("Arial", 16), fg = "white", bg = "#222222").pack(pady = 5)
        tk.Label(final, text = msg, font = ("Arial", 16, "italic"), fg = "#00FF00", bg = "#222222").pack(pady = 10)

        tk.Button(final, text = "Jugar otra vez", font = ("Arial", 14), bg = "#28a745", fg = "white",
                  command = lambda: [final.destroy(), juego.destroy(),iniciar_ventana_inicio()]).pack(pady = 10)
        tk.Button(final, text = "Salir", font = ("Arial", 14), bg = "#FF0000", fg = "white",
                  command = lambda: [final.destroy(), juego.destroy()]).pack(pady = 10)

        def closing():
            juego.attributes("-disabled", False)
            final.destroy()

        final.protocol("WM_DELETE_WINDOW", closing)

    # Asociar clicks
    for i in range(FILAS):
        for j in range(COLUMNAS):
            lbl = labels[i][j]
            lbl.bind("<Button-1>", lambda e, i=i, j=j: check_click(i, j))
            #blind asocia un evento de click para ejercutar las intrucciones que se escriban posteriormente
            #lambda crea una funcion rapida, e recibe el evento y se fijan las coordenadas i,j 
            #lambda sirve para que cada carta recuerde su posición en la matriz, y podamos voltear la carta correcta al hacer clic

    juego.mainloop()

# -------------------------------
def iniciar_ventana_inicio():
    root = tk.Tk()
    root.title("Memoria de Halloween")
    root.geometry("700x500")
    root.resizable(True, True)
    root.configure(bg="#222222")

    titulo = tk.Label(root, text=" MEMORAMA 👻",
                      font=("Arial", 24, "bold"), fg="#FF7518", bg="#222222")
    titulo.pack(pady=50)

    tk.Button(root, text="Fácil", font=("Arial", 16), width=20,
              bg="#28a745", fg="white", command=lambda: [root.destroy(), iniciar_juego("Fácil")]).pack(pady=10)
    tk.Button(root, text="Medio", font=("Arial", 16), width=20,
              bg="#ffc107", fg="white", command=lambda: [root.destroy(), iniciar_juego("Medio")]).pack(pady=10)
    tk.Button(root, text="Difícil", font=("Arial", 16), width=20,
              bg="#dc3545", fg="white", command=lambda: [root.destroy(), iniciar_juego("Difícil")]).pack(pady=10)

    root.mainloop()

# Ejecutar
iniciar_ventana_inicio()
