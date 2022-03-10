
class Chatbox {
    constructor() {
        this.args = {
            openButton:document.getElementById('chatbox_button'), 
            chatBox: document.querySelector('.chatbox__support') ,
            sendButton: document.querySelector('.send__button')
        }

        this.state = true;
        this.messages = [];
    }

    display() {
        const {openButton, chatBox, sendButton} = this.args;
        
         addEventListener('click', () => this.toggleState(chatBox))

        sendButton.addEventListener('click', () => this.onSendButton(chatBox))
        
        const node = chatBox.querySelector('input');
        node.addEventListener("keyup", ({key}) => {
            if (key === "Enter") {
                this.onSendButton(chatBox)
            }
        })
    }

    toggleState(chatbox) {
        this.state = !this.state;

        // shows or hides the chat box  
        if(this.state) {
            chatbox.classList.add('chatbox--active')
        } else {
            chatbox.classList.remove('chatbox--active')
        }
        
    }
    onSendButton(chatbox) {
        var textField = chatbox.querySelector('input');
        let text1 = textField.value
        if (text1 === "") {
            return;
        }

        let msg1 = { name: "User", message: text1 }
        this.messages.push(msg1);

        // 'http://127.0.0.1:5000/predict 
        fetch($SCRIPT_ROOT + '/predict', {
            method: 'POST',
            body: JSON.stringify({message: text1}),
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },

        })
        .then(r => r.json())
        .then(r => {
            let msg2 = { name: "Phil", message: r.answer };
            this.messages.push(msg2);


            this.updateChatText(chatbox)
            console.log('request returned')
            textField.value = ''
      }).catch((error) => {
          console.error('Error:', error);
          this.updateChatText(chatbox)
          textField.value = ''
      });
    
    }

    updateChatText(chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function(item, ) {
            console.log(item)
            if (item.name === "Phil")
            {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>'
            console.log('I am the visitor')
            }
            else
            {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>'
            console.log('I am the operator')
            }
        }
    );

    const chatmessage = chatbox.querySelector('.chatbox__messages');
    chatmessage.innerHTML = html;



    }



}
const chatbox = new Chatbox();
openButton = document.getElementById('chatbox_button');
console.log(openButton)
chatBox = document.querySelector('.chatbox__support')
console.log(chatBox)
sendButton = document.querySelector('.send__button')
console.log(sendButton)
chatbox.display();
