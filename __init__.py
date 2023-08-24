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
          host = "mysql-novato.alwaysdata.net",
          user = "novato",
          password = "-jP7NGy3-L-LkcK",
          database='novato_chat'
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

        # #SE ESCRIBE EL TEXTO DE LA RESPUESTA OBTENIDA DE LA LIBRERIA
        # f = open("texto.txt", "w")
        # f.write(respuesta)
        # f.close()

        #RETORNAMOS EL STATUS EN UN JSON
        return jsonify({"status": "success"}, 200)

#INICIAMSO FLASK
if __name__ == "__main__":
    app.run(debug=True)
