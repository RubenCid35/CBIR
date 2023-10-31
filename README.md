# Content Based Image Retrival: AAPI
Este repositorio contiene el código para la experimentación con diferentes
sistemas para la recuperación de imágenes. Se plantea realizar experimentos 
con la mezcla de parámetros y métodos.

Para un sistema C-B IR, se diferencia 3 partes importantes:
1. Creación de Bases de Datos con imágenes.
2. Extracción de Características: extraer el contenido de las imágenes para poder comparar
3. Comparación, Similaridad y Distancia entre contenidos de imágenes.

Este sistema permitirá obtener resultados como el siguiente:
![](docs/result_orb.png)

## Conjunto de Datos
Para la realización de la práctica, se ha tomado un subconjunto del dataset 'Universal Image Embeddings'
de Kaggle. Este dataset se componen de 11 clases diferentes y de imágenes de 128 x 128. Se ha tomado
este dataset debido a que contiene imágenes de buena calidad y clases suficientemente diferenciadas para 
no producir error al evaluarlas. Se puede acceder mediante el [siguiente enlace](https://www.kaggle.com/datasets/rhtsingh/google-universal-image-embeddings-128x128).

Para el subconjunto, se han tomado 50 imágenes de cada clase para el entrenamiento y la base de datos. 
Para el testeo del sistema y realizar queries se han tomado 10 de cada clase.

## Extración de Características.
Para los experimentos, se plantea usar con los siguientes métodos o algoritmos:

* [ ] Uso de Histograma de Color y Escala de Gris
* [ ] Descriptores SIFT y ORB. Detectores de Manchas Harris.
* [ ] Redes Neuronales Convolucionales: Usar las capas convolucionales o arquitectura de encoders-decorders
* [ ] Información de Textura


Se puede probar a aplicar PCA en caso de tener descriptores o vectores muy amplios. Otra forma será 
tomar solamente los N primeras posiciones del vector.

## Comparación y Matching
Para los experimentos, se plantea usar con los siguientes métodos o algoritmos:

* [ ] BruteForce Matching: OpenCV. Fuerza Bruta
* [ ] FlaanBasedMatching: OpenCV. Parecido al anterior
* [ ] Local Sensitive Hashing

Modelo Final: Bag of Words, Uso de TD-IDF (ver referencia), otro


