# coding=utf-8
from flask import Flask, request, jsonify 
import json 
import requests
import objectpath
import os

app = Flask(__name__) 
port = int(os.getenv("PORT", 9009)) #definicion de puerto de salida

@app.route('/', methods=['POST']) 
def index(): 
  
	postRece = json.loads(request.get_data())
	intent = str(postRece['nlp']['intents'][0]['slug']) #Se obtiene el nombre del intent desde el post de Recast
	skill = str(postRece['conversation']['skill']) #Se obtiene el nombre del skill desde el post de Recast
	print(skill)
	print(intent)
 
	if intent == "intentname" and skill == "lskillname": #Si el intent y el skill es el esperado
			entity = str(postRece['nlp']['entities']['entity_name'][0]['raw']) #Obtengo el nombre de la entidad (Si e necesaria para hacer la llamada a HANA)
			jsonData  = ExecuteGet("https://xs01b14ae55f1.us1.hana.ondemand.com/recast1/recast1_service.xsodata/QUESTION2?$format=json&$filter=FILTROUNO eq '"+entity+"'") #Se hace el request a un XSJS con los parámetros necesarios para hacer la consulta
			data = processData(jsonData) #Envía la respuesta de HANA y la procesa para cumplir con el formato de Recast
	
	else: # En caso de no ser una opción validad, mandamos un mensaje fijo.
		data = jsonify( 
		status=200, 
		replies=[{'type': 'text','content': 'Pendón, no entendí. ¿Podrías refrasear tu pregunta?'}],conversation={'memory': { 'key': 'value' }} ) #Esta es la estructura de un mensaje simple en Recast, referir a: https://recast.ai/docs/concepts/structured-messages para conocer todos los formatos de mensaje permitidos
		
	print(data)
  
	return data #Regresa la respuesta a Recast
   
  
def ExecuteGet(request): #Ejecuta el request a HANA
  print(request)
	#########################################
  URL = request
	
  # defining a params dict for the parameters to be sent to the API
  HEADERS = {'Authorization': "Basic {Base 64}"} #Agregar Autenticación Básica (Usuario y contraseña) de la base de datos en formato Base64
	 
  # sending get request and saving the response as response object
  r = requests.get(url=URL,headers=HEADERS)
  print(str(r.json()))
  # extracting data in json format
  return r.json()
  #############################
def processData(jsonData):
	answers = {}
	answer = ''
	results = len(jsonData['d']['results'])
	if str(jsonData['d']['results'][0]['PARAMETRO']) == "Algún Parámetro": #Si lo recibido de HANA tiene cierto formato, entonces proceso la información para envialo a Recast
		answer = jsonify( 
		status=200, 
		replies=[{
		  "type":"card",
		  "content":{
		  "title": "Gráfico",
		  "imageUrl":"Image_URL",
		  "subtitle": "Información recibida "+str(jsonData['d']['results'][0]['PARAMETRO']),  #Este es un ejemplo de como agregar la información recibida en HANA y agregarlo a un objeto en Recast, favor de referirse a:  https://recast.ai/docs/concepts/structured-messages para conocer todos los formatos de mensaje permitidos
		  "buttons": [
			{
			  "title": "Abrir Gráfica",
			  "type": "web_url",
			  "value": "Image_URL" 
			}
			]
		  
		  }
		  
		  }], 
		conversation={ 
		  'memory': { 'key': 'value' } 
		} 
		)
	else: #Si no
		answer = jsonify( 
		status=200, 
		replies=[{ 
		  'type': 'text', 
		  'content': "Cualquier respuesta", 
		}], 
		conversation={ 
		  'memory': { 'key': 'value' } 
		} 
		)
	
	return answer
	
	
	
@app.route('/errors', methods=['POST']) 
def errors(): 
  json.loads(request.get_data())
  return jsonify(status=200) 
 
app.run(host='0.0.0.0',  port=port) #importante indicar host para deployment en plataforma

#cf login
#API Endpoint:https://api.cf.eu10.hana.ondemand.com
#cf push botRecast manifest file C:\Users\i861443\Desktop\python SCP\Recast\manifest.yml
#requirements.txt para instalación de imports