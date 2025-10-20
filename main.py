import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random

import os

import pygame#librería para poder ponerle música 

pygame.mixer.init()

def reproducir_musica(ruta, volumen=0.5):
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.set_volume(volumen)
    pygame.mixer.music.play(-1)  # -1 = la música se reproduce en bucle

# Configuración
#tamaño de cada carta
ANCHO_BOTON = 80
ALTO_BOTON = 80
FILAS, COLUMNAS = 6, 6 #cartas en el tablero
TOTAL_PAREJAS = (FILAS * COLUMNAS) // 2 #formar parejas

imagenes = [
    "Imagenes/1.jpg", "Imagenes/2.jpg", "Imagenes/3.jpg", "Imagenes/4.jpg", "Imagenes/5.jpg", "Imagenes/6.jpg", "Imagenes/7.jpg",
    "Imagenes/8.jpg", "Imagenes/9.jpg", "Imagenes/10.png", "Imagenes/11.jpg", "Imagenes/12.jpg", "Imagenes/13.jpg", "Imagenes/14.jpg",
    "Imagenes/16.jpg", "Imagenes/17.jpg", "Imagenes/18.jpg", "Imagenes/15.jpg"
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
    
    fondo = Image.open(os.path.join(BASE_DIR, "Imagenes/fondo.png")).resize((ANCHO_BOTON, ALTO_BOTON))

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
    # --- FUNCIONES DE ANIMACIÓN ---
    # -------------------------------
    def animacion_aparicion(widget, delay=0):
        """Animación de aparición gradual"""
        widget.place_forget() if hasattr(widget, 'place_info') and widget.place_info() else None
        widget.pack_forget() if hasattr(widget, 'pack_info') and widget.pack_info() else None
        widget.grid_forget() if hasattr(widget, 'grid_info') and widget.grid_info() else None
        
        widget.place(relx=0.5, rely=0.5, anchor='center')
        widget.configure(alpha=0.0)
        
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                alpha += 0.1
                try:
                    widget.configure(alpha=alpha)
                    juego.after(30, lambda: fade_in(alpha))
                except:
                    pass
        
        juego.after(delay, fade_in)

    def animacion_voltear(widget, nueva_imagen, es_revelado):
        original_width = ANCHO_BOTON
        steps = 10
        
        def animate_step(step):
            if not juego.winfo_exists(): return
            if step <= steps:
                new_width = int(original_width * (1 - abs(step - steps / 2) / (steps / 2)))
                if new_width < 1: new_width = 1
                
                if step == steps // 2:
                    widget.config(image=nueva_imagen)
                
                # Usar place para controlar el tamaño sin afectar el grid
                widget.place(in_=widget.master, anchor="center", relx=.5, rely=.5, width=new_width)
                
                juego.after(15, lambda: animate_step(step+1))
            else:
                widget.place(in_=widget.master, anchor="center", relx=.5, rely=.5, width=original_width, height=ALTO_BOTON)
                widget.revelado = es_revelado
        
        animate_step(0)

    def animacion_acierto(widget1, widget2):
        widget1.master.config(bg="#FFD700") # Color dorado para acierto
        widget2.master.config(bg="#FFD700")

    def animacion_error(widget1, widget2):
        original_color = "#444444"
        widget1.master.config(bg="#DC3545") # Color rojo para error
        widget2.master.config(bg="#DC3545")
        
        def restaurar_color():
            if juego.winfo_exists():
                widget1.master.config(bg=original_color)
                widget2.master.config(bg=original_color)

        juego.after(600, restaurar_color)

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
    def voltear_todas_con_animacion():
        if not juego.winfo_exists(): return
        
        def voltear_progresivo(idx=0):
            if not juego.winfo_exists(): return
            if idx < FILAS * COLUMNAS:
                i = idx // COLUMNAS
                j = idx % COLUMNAS
                lbl = labels[i][j]
                animacion_voltear(lbl, fondo_tk, False)
                juego.after(30, lambda: voltear_progresivo(idx + 1))
        
        voltear_progresivo()

    juego.after(tiempo_memoria, voltear_todas_con_animacion) #luego de tiempo_memoria, voltea las cartas

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
        
        animacion_voltear(lbl, lbl.imagen_real, True)

        lbl.config(image=lbl.imagen_real) #voltea la carta
        lbl.revelado = True

        if not primer_click[0]: #verifica si todavía no hay una carta seleccionada como primera.
            primer_click[0] = (i, j) #Si no hay primer clic, guarda las coordenadas de la carta que se acaba de clicar
        else: #Si ya hay un primer_click, entonces esta carta es la segunda que el jugador selecciona.
            segundo_click[0] = (i, j)
            bloqueo[0] = True #Bloquea al jugador de seleccionar más cartas mientras se comparan
            juego.after(500, verificar_pareja) #Espera 500 ms (medio segundo) y luego llama a la función verificar_pareja.

    def verificar_pareja():
        if not juego.winfo_exists(): return
        if primer_click[0] is None or segundo_click[0] is None:
            bloqueo[0] = False
            return

        i1, j1 = primer_click[0]
        i2, j2 = segundo_click[0]
        lbl1 = labels[i1][j1]
        lbl2 = labels[i2][j2]

        intentos[0] += 1

        if lbl1.nombre_imagen == lbl2.nombre_imagen:
            encontradas[0] += 1
            if intentos[0] <= 18:
                puntaje[0] += 1
            animacion_acierto(lbl1, lbl2)
            if encontradas[0] == TOTAL_PAREJAS:
                bloqueo[0] = True
                juego.after(5000, finalizar_juego)
        else:
            animacion_error(lbl1, lbl2)
            # Esperar a que la animación de error sea visible antes de voltear
            juego.after(600, lambda: [
                animacion_voltear(lbl1, fondo_tk, False) if juego.winfo_exists() else None,
                animacion_voltear(lbl2, fondo_tk, False) if juego.winfo_exists() else None
            ])

        primer_click[0] = None
        segundo_click[0] = None
        
        # Desbloquear después de que terminen las animaciones de volteo
        juego.after(500, lambda: bloqueo.__setitem__(0, False) if juego.winfo_exists() else None)


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

        final = tk.Toplevel(juego)
        final.title("Fin del juego")
        final.geometry("400x400")
        final.configure(bg = "#222222")

        final.transient(juego) #Para asegurarse de que la ventana se genere sobre el juego previo
        final.grab_set() #Para dirigir todas las acciones hacia esta ventana

        tk.Label(final, text = "Juego Terminado!", font=("Arial", 24, "bold"), fg="#FF7518", bg="#222222").pack(pady = 20)
        tk.Label(final, text = f"Puntaje: {puntaje[0]}", font = ("Arial", 16), fg = "white", bg = "#222222").pack(pady = 5)
        tk.Label(final, text = f"Intentos: {intentos[0]}",font = ("Arial", 16), fg = "white", bg = "#222222").pack(pady = 5)
        tk.Label(final, text = msg, font = ("Arial", 16, "italic"), fg = "#00FF00", bg = "#222222").pack(pady = 10)

        tk.Button(final, text = "Jugar otra vez", font = ("Arial", 14), bg = "#28a745", fg = "black",
                  command = lambda: [final.destroy(), juego.destroy(),iniciar_ventana_inicio()]).pack(pady = 10)
        tk.Button(final, text = "Salir", font = ("Arial", 14), bg = "#FF0000", fg = "black",
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
    reproducir_musica("Imagenes/musica.mp3")
    root = tk.Tk()
    root.geometry("700x500")

    #Centrar Ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (700 // 2)
    y = (root.winfo_screenheight() // 2) - (500 // 2)
    root.geometry(f"700x500+{x}+{y}")


    # Crear canvas
    canvas = tk.Canvas(root, width=700, height=500)
    canvas.pack(fill="both", expand=True)

    # imagen de fondo
    fondo_img = Image.open("Imagenes/3.png").resize((700, 500))
    fondo_tk = ImageTk.PhotoImage(fondo_img)
    canvas.create_image(0, 0, image=fondo_tk, anchor="nw")

    # imagen de botones
    img_facil = Image.open("Imagenes/facil.png").resize((200, 50))
    img_normal = Image.open("Imagenes/normal.png").resize((200, 50))
    img_dificil = Image.open("Imagenes/dificil.png").resize((200, 50))

    btn_img = ImageTk.PhotoImage(img_facil)
    btn_img1 = ImageTk.PhotoImage(img_normal)
    btn_img2 = ImageTk.PhotoImage(img_dificil)

    # Guardar referencias para que no se borren
    canvas.btn_imgs = [fondo_tk, btn_img, btn_img1, btn_img2]

    # Funcion para cada botón
    def jugar_facil(event=None):
        print("Iniciar modo FÁCIL")
        root.destroy()
        iniciar_juego("Fácil")

    def jugar_medio(event=None):
        print("Iniciar modo NORMAL")
        root.destroy()
        iniciar_juego("Medio")

    def jugar_dificil(event=None):
        print("Iniciar modo DIFÍCIL")
        root.destroy()
        iniciar_juego("Difícil")

    # poner las imagenes de los botones sobre el fondo
    boton_facil = canvas.create_image(350, 290, image=btn_img)
    boton_normal = canvas.create_image(350, 350, image=btn_img1)
    boton_dificil = canvas.create_image(350, 410, image=btn_img2)

    # Vincular a funciones
    canvas.tag_bind(boton_facil, "<Button-1>", jugar_facil)
    canvas.tag_bind(boton_normal, "<Button-1>", jugar_medio)
    canvas.tag_bind(boton_dificil, "<Button-1>", jugar_dificil)

    root.mainloop()

# Ejecutar
iniciar_ventana_inicio()
