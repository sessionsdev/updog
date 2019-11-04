
let currentChatId = null;

const setHeaderImage = () => {
    const pageElement = document.querySelector('#self-image');
    let imageElement = document.createElement('img');
    imageElement.classList.add('icon-img');
    imageElement.setAttribute('src', "http://lorempixel.com/output/animals-q-c-284-204-8.jpg");
    imageElement.setAttribute('alt', 'Puppy Icon Image for user');
    pageElement.appendChild(imageElement);
}




const wrapMessages = (message, time, sent, oldMessage=true) => {

    let pageElement = document.querySelector('#main-chat-wrap');
    let div1Element = document.createElement('div');
    let div2Element = document.createElement('div');
    let paragrapeElement = document.createElement('p');
    let timeElement = document.createElement('p')


    div1Element.classList.add('message-wrap');
    div2Element.classList.add('message');
    div2Element.classList.add(sent ? 'out' : 'in')
    paragrapeElement.classList.add('mssg');
    timeElement.classList.add('mssg-time')


    if(oldMessage){
        pageElement.appendChild(div1Element);
    }
    else{
        pageElement.insertBefore(div1Element, pageElement.firstChild)
    }
    div1Element.appendChild(div2Element);
    div2Element.appendChild(paragrapeElement)
    div2Element.appendChild(timeElement)
    paragrapeElement.innerHTML = `${message}`
    timeElement.innerHTML = `${time}`

}



const addMessages = (messages) =>{
    let pageElement = document.querySelector('#main-chat-wrap');
    let userId = document.querySelector('.convo').dataset.user_id
    let sent = false
    pageElement.innerHTML = ''
    messages.forEach(message => {
        if (message.sender_id == userId){
            sent = true
            } else {
                sent = false
            }
        wrapMessages(message.body, message["time-stamp"], sent);
    })
    }


// setInterval( () =>{
//     if (currentChatId !== null && currentUserId !== null) {
//         retrieveMessages(currentChatId, currentUserId)
//         let pageElement = document.querySelector('#main-chat-wrap');
//         pageElement.innerHTML = ''
//     }

// }, 2000)

const retrieveMessages = (chat_id, user_id) => {
    const url = `/api/chats/${chat_id}/messages?user_id=${user_id}`
    fetch(url, {
        method: 'GET'
    }).then(res => res.json())
      .then(data => addMessages(data))
}


const convoClick = (event) => {

    // population form chat_id input
    const clicked = event.currentTarget;
    const dataAttributes = clicked.dataset;
    const chat_id = dataAttributes.chat_id;
    const user_id = dataAttributes.user_id;
    document.querySelector('#sndr-chat_id').value = chat_id;
    currentChatId = chat_id
    currentUserId = user_id

    // retreive messages for clicked conversation
    retrieveMessages(chat_id, user_id);
}


const conversationElements = document.getElementsByClassName("convo");

for(let i =0; i < conversationElements.length; i++){
    conversationElements[i].addEventListener('click', convoClick, false);
}


const createNewChat = () =>{
    const recipientEmail = document.getElementById('new-chat').value
    const senderId = document.getElementById('chat-creator').value

    const url = '/api/chats'
    fetch (url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'email': recipientEmail,
            'sender_id': senderId

        })
    }).then(window.location.reload())
}



const submitNewMessage = () =>{

    // collection data needed for POST request
    const newMessage = document.getElementById('new-message').value;
    const chat_id = document.querySelector('#sndr-chat_id').value;
    const user_id = document.querySelector('#sndr-name').value;

    // POST request to create message
    const url = `/api/chats/${chat_id}/messages?user_id=${user_id}`
    fetch (url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'body': newMessage
        })
    })

    //  Add message to DOM
    .then(res => res.json())
    .then(data => {
        wrapMessages(data.body, data['time-stamp'], sent=true, oldMessage=false);
        document.querySelector('#new-message').value = '';
        document.querySelector(`div.convo[data-chat_id="${chat_id}"] p.mssg`).innerHTML = data.body
})

}


    
setHeaderImage()