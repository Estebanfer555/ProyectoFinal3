#PROYECTO FINAL - PROCESAMIENTO DE IMAGENES PARA CLASIFICACION DE LIMONES

#Librerias 
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow
from PyQt5.QtWidgets import QFileDialog
import cv2
import numpy as np
import imutils
import serial 
import time

#Variables

#Contadores
limon_counter=0
limon_ama_counter= 0
limon_ver_counter = 0
limon_def_counter = 0
kg_tot = 0
kg_exp = 0
#Limites de los colores
min_am = np.array([22,21,0])
max_am = np.array([33,255,255])
min_ver = np.array([35,50,0])
max_ver = np.array([89,255,255])
min_df = np.array([0,150,80])
max_df = np.array([20,255,205])

#Leds puerto serial
la = 'A'
lv = 'V'
lr = 'R'

#Comunicacion con puerto serial
esp = serial.Serial("COM9", 9600)

#Clase para iniciar la interfaz
class Screen (QMainWindow):
    def __init__(self):
        super(Screen, self).__init__()
        loadUi("D:\Proyecto Final\interfazPF.ui", self) #Cargar archivo con la interfaz

        #Funciones de los botones
        self.cargar.clicked.connect(self.cargarImagen)
        self.capturar.clicked.connect(self.tomarFoto)
        self.clasificar.clicked.connect(self.clasificarFoto)
        self.iniciarVideo.clicked.connect(self.start_video)
        self.pararVideo.clicked.connect(self.cancel)

    #Funciones para imagen
    def cargarImagen(self):
        global filename
        global imagen
        filename = QFileDialog.getOpenFileName(filter="Image (*.*)")[0]
        imagen = cv2.imread(filename)
        self.setPhotoEntrada(imagen)
    
    def tomarFoto(self):
        global imagen
        #abrir la camara
        cap= cv2.VideoCapture(0) #0 es numero de webcam
        #Definir dimenciones
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920) #Ancho
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080) #Alto
        #tomar una imagen
        ret, frame = cap.read()
        #Guardar imagen
        cv2.imwrite('D:/frame.jpg',frame)
        #Guardar en variable
        imagen=cv2.imread('D:/frame.jpg')
        #Liberamos la camara
        cap.release()
        #Visualizamos imagen
        self.setPhotoEntrada(imagen)

    def setPhotoEntrada(self, image):
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        imagen = imagen.scaled(1000, 470, Qt.KeepAspectRatio)
        self.imgEntrada.setPixmap(QtGui.QPixmap.fromImage(imagen))
    
    #Funcion para detectar color Imagen 
    def clasificarFoto(self):
    
        #Variables con limites de color para imagen
        #amarilloBajo= np.array([25,150,0],np.uint8)
        #amarilloAlto= np.array([40,255,255],np.uint8)
        #verdeBajo= np.array([31,150,0],np.uint8) 
        #verdeAlto= np.array([60,210,250],np.uint8)
        #defectoBajo= np.array([0,150,100],np.uint8) 
        #defectoAlto= np.array([20,210,250],np.uint8)

        #Conversion a entorno HSV 
        imageHSV = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV) 
        #Buscar rangos de amarillo
        imageB= cv2.inRange(imageHSV,min_am,max_am)
        #Encontrar contornos
        contornos, hierarchy = cv2.findContours(imageB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contornos:
            area= cv2.contourArea(cnt)
            
            if area > 75000:
                
                print('Area: ' +str(area))    

                M = cv2.moments(cnt)
                if (M["m00"]==0): M["m00"]=1
                x = int(M["m10"]/M["m00"])
                y = int(M['m01']/M['m00'])
                    
                cv2.circle(imagen, (x,y), 7, (0,255,0), -1)
                #font = cv2.FONT_HERSHEY_SIMPLEX
                #cv2.putText(image, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,255),1,cv2.LINE_AA)

                cv2.drawContours(imagen,[cnt],0,(255,0,0),5)

                x1,y1,w1,h1 = cv2.boundingRect(cnt)
                diampx = (w1 + h1) / 2
                diam= round((diampx/10.30),1)
                print('Limon Aceptado', 'pix=' + str(diam))
                cv2.rectangle(imagen, (x1,y1), (x1+w1,y1+h1), (0,255,255), 5)
                cv2.putText(imagen, 'Amarillo:'+str(round(diam))+'mm', (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,255), 5)
                cv2.line(imagen,(x,y),(x,y1),(255,255,255), 3)
                

                #Imprimir label
                self.label_estado.setText('Limon Amarillo')
                self.label_diam.setText(str(diam)+' mm')
                self.label_clasificacion.setText('Exportación')

                #Encender led Amarillo
                esp.write(la.encode('ascii'))
                time.sleep(2)
            
            #Comprobar si es verde
            else:
                #Buscar rangos de VERDE
                imageB= cv2.inRange(imageHSV,min_ver,max_ver)
                #Encontrar contornos
                contornos, hierarchy = cv2.findContours(imageB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for cnt in contornos:
                    area= cv2.contourArea(cnt)
                    
                    if area > 75000:
                        
                        print('Area: ' +str(area))    

                        M = cv2.moments(cnt)
                        if (M["m00"]==0): M["m00"]=1
                        x = int(M["m10"]/M["m00"])
                        y = int(M['m01']/M['m00'])
                            
                        cv2.circle(imagen, (x,y), 7, (0,255,0), -1)
                        #font = cv2.FONT_HERSHEY_SIMPLEX
                        #cv2.putText(image, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,255),1,cv2.LINE_AA)

                        cv2.drawContours(imagen,[cnt],0,(255,0,0),5)

                        x1,y1,w1,h1 = cv2.boundingRect(cnt)
                        diampx = (w1 + h1) / 2
                        diam= round((diampx/10.30),1)
                        print('Limon Verde', 'pix=' + str(diam))
                        cv2.rectangle(imagen, (x1,y1), (x1+w1,y1+h1), (0,255,0), 5)
                        cv2.putText(imagen, 'Verde:'+str(round(diam))+ 'mm', (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 5)
                        cv2.line(imagen,(x,y),(x,y1),(255,255,255), 3)

                        #Imprimir label
                        self.label_estado.setText('Limon Verde')
                        self.label_diam.setText(str(diam)+' mm')
                        self.label_clasificacion.setText('Local')
                        
                        #Encender led Verde
                        esp.write(lv.encode('ascii'))
                        time.sleep(2)

                #Comprobar si es defecto 
                else:
                    #Buscar rangos de marron
                    imageB= cv2.inRange(imageHSV,min_df,max_df)
                    #Encontrar contornos
                    contornos, hierarchy = cv2.findContours(imageB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    for cnt in contornos:
                        area= cv2.contourArea(cnt)
                        
                        if area > 25000:
                            
                            print('Area: ' +str(area))    

                            M = cv2.moments(cnt)
                            if (M["m00"]==0): M["m00"]=1
                            x = int(M["m10"]/M["m00"])
                            y = int(M['m01']/M['m00'])
                                
                            cv2.circle(imagen, (x,y), 7, (0,255,0), -1)
                            #font = cv2.FONT_HERSHEY_SIMPLEX
                            #cv2.putText(image, '{},{}'.format(x,y),(x+10,y), font, 0.75,(0,255,255),1,cv2.LINE_AA)

                            cv2.drawContours(imagen,[cnt],0,(255,0,0),5)

                            x1,y1,w1,h1 = cv2.boundingRect(cnt)
                            diampx = (w1 + h1) / 2
                            diam= round((diampx/10.30),1)
                            print('Limon Verde', 'pix=' + str(diam))
                            cv2.rectangle(imagen, (x1,y1), (x1+w1,y1+h1), (0,0,255), 5)
                            cv2.putText(imagen, 'Defecto:'+str(round(diam))+ 'mm', (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 5)
                            cv2.line(imagen,(x,y),(x,y1),(255,255,255), 3)

                            #Imprimir label
                            self.label_estado.setText('Limon Maduro')
                            self.label_diam.setText(str(diam)+' mm')
                            self.label_clasificacion.setText('Rechazado')
                            
                            #Encender led Rojo
                            esp.write(lr.encode('ascii'))
                            time.sleep(2)

                    else:
                        if area > 3000:
                            print('Limón Rechazado')

                            #Imprimir label
                            #window.labelPrueba.setText('Limon Rechazado')

        self.setPhotoSalida(imagen)
    
    def setPhotoSalida(self, image):
        frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imagen = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)
        imagen = imagen.scaled(1000, 470, Qt.KeepAspectRatio)
        self.imgSalida.setPixmap(QtGui.QPixmap.fromImage(imagen))


    #Funciones para Video
    def start_video(self):
        self.WorkProyecto = WorkProyecto()
        self.WorkProyecto.start()
        self.WorkProyecto.Imageupd.connect(self.Imageupd_slot)

    def Imageupd_slot(self, Image):
        self.video.setPixmap(QPixmap.fromImage(Image))
        #self.label_camara.setStyleSheet("border: 2px solid black;")
        self.label_limones_total.setText(str(self.WorkProyecto.contadorTotal()))
        self.label_limones_export.setText(str(self.WorkProyecto.contadorAmarillo()))
        self.label_limones_local.setText(str(self.WorkProyecto.contadorVerde()))
        self.label_limones_rechazados.setText(str(self.WorkProyecto.contadorDefecto()))
        self.label_kg_limones_tot.setText(str(round(self.WorkProyecto.kgTotal()/11, 2)))
        self.label_kg_limones_exp.setText(str(round(self.WorkProyecto.kgExp()/11, 2)))

    def cancel(self):
        self.WorkProyecto.stop()
        self.video.clear()

#Clase para el procesamiento de imagenes    
class WorkProyecto(QThread): #QTrend para uso de hilos y poder ejecutar interfaz y procesamiento en paralelo
    Imageupd = pyqtSignal(QImage)
    def run(self):
        self.hilo_corriendo = True
        
        self.limon_counter= limon_counter
        self.limon_ama_counter= limon_ama_counter
        self.limon_ver_counter= limon_ver_counter
        self.limon_def_counter= limon_def_counter
        self.kg_tot= kg_tot
        self.kg_tot= kg_exp


        cap = cv2.VideoCapture(0)
        #cap = cv2.VideoCapture('D:/Proyecto Final/video2.avi')
        while self.hilo_corriendo:
            ret, frame = cap.read()
            
            if ret:

                area_pts = np.array([[50, 50], [600, 50], [600, 450], [50, 450]]) #para especificar puntos de la region de interes (calculo a pruba y error)
    
                #con ayuda de una imagen auxiliar determinamos el area sobre la cual actuara el detector de movimiento
                imAux = np.zeros(shape=(frame.shape[:2]),dtype= np.uint8) #debe tener mismo tamaño que frame 
                imAux = cv2.drawContours(imAux, [area_pts], -1, (255), -1) #llenar el area de interes de blanco con -1
                image_area = cv2.bitwise_and(frame, frame, mask=imAux) #para ver lo del video en el rectangulo

                imgF = cv2.blur(frame, (9,9))
                #imgF = cv2.GaussianBlur(img, (15, 15), 15)
                imgHSV = cv2.cvtColor(imgF, cv2.COLOR_BGR2HSV)
                imgB = cv2.inRange(imgHSV, min_am, max_am)

                # Encontramos los contornos presentes de fgmask, para luego basándonos en su área poder determinar si existe movimiento (autos)
                contornos = cv2.findContours(imgB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

                for cnt in contornos:
                    if cv2.contourArea(cnt) > 1500: 
                        x, y, w, h = cv2.boundingRect(cnt)
                        diamPx = (w + h) / 2
                        diam_mm = round ((diamPx / 4.52), 1)
                        cv2.rectangle(frame, (x,y), (x+w, y+h),(0,255,255),2)
                        #cv2.putText(frame, 'Amarillo:'+str(round(diamPx)), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                        cv2.putText(frame, 'Amarillo:'+str(diam_mm), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)
                        
                        # Si el limon ha cruzado entre 300 y 400, se incrementará en 1 el contador de autos
                        if 300 < ((y)) < 400:
                            #global limon_ama_counter
                            #global limon_counter
                            self.limon_ama_counter= self.limon_ama_counter + 1
                            self.limon_counter= self.limon_counter + 1
                            #self.kg_tot= self.kg_tot + 1
                            print(self.limon_counter)
                            cv2.line(frame,(50,350),(600,350), (0,255,0), 3) #linea en la mitad del area aproximadamente
                            print(x, y, w, h)

                            
                          
                    #Comprobar si es verde
                    imgB = cv2.inRange(imgHSV, min_ver, max_ver)
                    contornos = cv2.findContours(imgB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
                    for cnt in contornos:
                        if cv2.contourArea(cnt) > 1500: 
                            x, y, w, h = cv2.boundingRect(cnt)
                            diamPx = (w + h) / 2
                            diam_mm = round ((diamPx / 4.52), 1)
                            cv2.rectangle(frame, (x,y), (x+w, y+h),(0,255,0),2)
                            cv2.putText(frame, 'Verde:'+str(diam_mm), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

                            if 300 < ((y)) < 400:
                                self.limon_ver_counter= self.limon_ver_counter + 1
                                self.limon_counter= self.limon_counter + 1
                                cv2.line(frame,(50,350),(600,350), (0,255,0), 3) #linea en la mitad del area aproximadamente
                                print(x, y, w, h)
                    
                    #Comprobar si es defecto
                    imgB = cv2.inRange(imgHSV, min_df, max_df)
                    contornos = cv2.findContours(imgB, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
                    for cnt in contornos:
                        if cv2.contourArea(cnt) > 500: 
                            x, y, w, h = cv2.boundingRect(cnt)
                            diamPx = (w + h) / 2
                            diam_mm = round ((diamPx / 4.52), 1)
                            cv2.rectangle(frame, (x,y), (x+w, y+h),(0,0,250),2)
                            cv2.putText(frame, 'Defecto:'+str(diam_mm), (x,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,250), 2)

                            if 300 < ((y)) < 400:
                                self.limon_def_counter= self.limon_def_counter + 1
                                self.limon_counter= self.limon_counter + 1
                                cv2.line(frame,(50,350),(600,350), (0,255,0), 3) #linea en la mitad del area aproximadamente
                                print(x, y, w, h)

                self.kg_tot = self.limon_counter
                self.kg_exp = self.limon_ama_counter
                
                #Visualizacion 
                cv2.drawContours(frame, [area_pts], -1, (255,0,255),2) #Visualización Area
                cv2.line(frame,(50,350),(600,350), (0,255,255), 1) #linea en la mitad del area aproximadamente
                             
                Image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                #flip = cv2.flip(Image, 1)
                convertir_QT = QImage(Image.data, Image.shape[1], Image.shape[0], QImage.Format_RGB888)
                pic = convertir_QT.scaled(920, 460, Qt.KeepAspectRatio)
                                
                self.Imageupd.emit(pic)

                

                
    def contornos(self):
        a = len(self.ctns)
        return a
    
    def contadorTotal(self):
        a = self.limon_counter
        return a

    def contadorAmarillo(self):
        b = self.limon_ama_counter
        return b

    def contadorVerde(self):
        c = self.limon_ver_counter
        return c

    def contadorDefecto(self):
        d = self.limon_def_counter
        return d

    def kgTotal(self):
        e = self.kg_tot
        return e
    
    def kgExp(self):
        f = self.kg_exp
        return f

    def stop(self):
        self.hilo_corriendo = False
        self.quit()
        

#Visualizar pantalla principal
app = QApplication(sys.argv)
principal= Screen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(principal)
widget.setFixedHeight(980)
widget.setFixedWidth(1920)

widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Saliendo")