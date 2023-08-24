#ChatBot inteligente con WhatsApp en Python
from flask import Flask, jsonify, request

app = Flask(__name__)

#CUANDO RECIBAMOS LAS PETICIONES EN ESTA RUTA
@app.route("/webhook/", methods=["POST", "GET"])
def webhook_whatsapp():
    #SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        #SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "tokenYeyo":
            #ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            #SI NO SON IGUALES LOS TOKEN RETORNAMOS UN MENSAJE DE ERROR
          return "Error de autentificacion."

    #RECIBIMOS TODOS LOS DATOS EN JSON
    data=request.get_json()
    #EXTRAEMOS EL NUMERO DE TELEFONO DEL EMISOR
    telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    #EXTRAEMOS EL TEXTO DEL MENSAJE ENVIADO
    mensaje=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    #EXTRAEMOS EL ID DE WHATSAPP DEL JSON
    idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
    #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL JSON
    timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    #ESCRIBIMOS EL NUMERO DE TELEFONO Y EL MENSAJE EN EL ARCHIVO TEXTO

    #SI HAY UN MENSAJE
    if mensaje is not None:
        #SE INICIALIZA RIVESCRIPT Y SE CARGA EL MENSAJE PARA OBTENER RESPUESTA
        from rivescript import RiveScript
        bot=RiveScript()
        bot.load_file('yeyo.rive')
        bot.sort_replies()

        #SE OBTIENE LA RESPUESTA
        respuesta=bot.reply("localuser",mensaje)
        respuesta=respuesta.replace("\\n","\\\n")
        respuesta=respuesta.replace("\\","")
        
        #CONECTAMOS A LA BASE DE DATOS
        import mysql.connector
        mydb = mysql.connector.connect(
          host = "mysql-xyrus.alwaysdata.net",
          user = "xyrus",
          password = "fmv7cqj@kbc9KEM2zvw",
          database='xyrus_chat'
        )
    
        mycursor = mydb.cursor()
    
        query="SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';"
        mycursor.execute("SELECT count(id) AS cantidad FROM registro WHERE id_wa='" + idWA + "';")

        cantidad, = mycursor.fetchone()
        cantidad=str(cantidad)
        cantidad=int(cantidad)
        if cantidad==0 :
            sql = ("INSERT INTO registro"+ 
            "(mensaje_recibido,mensaje_enviado,id_wa      ,timestamp_wa   ,telefono_wa) VALUES "+
            "('"+mensaje+"'   ,'"+respuesta+"','"+idWA+"' ,'"+timestamp+"','"+telefonoCliente+"');")
            mycursor.execute(sql)
            mydb.commit()

            #SE ENVIA LA RESPUESTA AL CLIENTE
            enviar(telefonoCliente,respuesta)

            #RETORNAMOS EL STATUS EN UN JSON
            return jsonify({"status": "success"}, 200)
        
def enviar(telefonoRecibe,respuesta):
  from heyoo import WhatsApp
  #TOKEN DE ACCESO DE FACEBOOK
  token='EAACrVLezN8EBO9POTOIIBwzeqoiZALNPpw4yQT4cZBmjcqjPOxulDuBZAZAyhXGDvj5zn3WxBNQVPrgKkEcprWQjttXOhelIGAbixMQDkRwUO6uesQ5UmWwPCt1oSBUyGEftvBuyJkNhDr4AyHl0v0R6SNbjjErdEPb5TCwmdPDWnU3PfZCMY9beXwBG51bittDPgVnfIrlPormlb9dQZD'
  #IDENTIFICADOR DE NÚMERO DE TELÉFONO
  idNumeroTeléfono='121737841012779'
  #INICIALIZAMOS ENVIO DE MENSAJES
  mensajeWa=WhatsApp(token,idNumeroTeléfono)
  telefonoRecibe=telefonoRecibe.replace("521","52")
  #ENVIAMOS UN MENSAJE DE TEXTO
  mensajeWa.send_message(respuesta,telefonoRecibe)

#INICIAMSO FLASK
if __name__ == "__main__":
    app.run(debug=True)
