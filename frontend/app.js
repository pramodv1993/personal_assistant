const venom = require('venom-bot');
const axios = require('axios');

venom.create({session: "mybot",
headless: true,
useChrome: false,
browserArgs:['--no-sandbox',
'--disable-setuid-sandbox'],
disableWelcome: true,
updatesLog: true,
autoClose: false,
multidevice: true
})
.then((client)=>start(client))
.catch((error)=>console.log(error))

function start(client){
  const myNumber = ""
  client.onMessage(async (message)=>{
    if (message.body){
      // console.log(`Received from ${message.from}: ${message.body}`)
      //get response from API
      query = message.body
      try{
        const response = await axios({
          method:'post',
          url:'http://localhost:8000/ask_ai',
          responseType: 'stream',
          params:{'query': query}
        });
        let buffer = "";
        response.data.on('data', async (chunk) =>{
          buffer += chunk.toString();
        });
        response.data.on('end', async () => {
          try{
            await client.sendText(message.from, buffer)
          }
          catch(error){
            await client.sendText(message.from, "Something failed when trying to retrieve answer:- " + error)
          }
        });
        response.data.on('error', async (err) => {
          await client.sendText(message.from, "Stream error while retrieving the answer", err);
        })
      }
      catch(error){
          await client.sendText(message.from, "Something failed when trying to retrieve answer:- " + error)
        }
      }
    });
}
