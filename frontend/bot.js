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
    console.log(message)
    if (message.body){
      console.log(`Received from ${message.from}: ${message.body}`)
      const result = await client.sendText(message.from, 'Welcome Venom')
      .then((result) => { console.log('Result:', result);
    })
    .catch((erro)=>{
      console.error("Error when sending: ", erro);
    });

    }
  });
}
