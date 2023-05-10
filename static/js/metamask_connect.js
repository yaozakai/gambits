var usernameField = null
var addressField = null
var connect_wallet_button = document.getElementById('connect-wallet')
    connect_wallet_button.addEventListener('click', connect)


var usernameField = document.getElementById('username-field')
var addressField = document.getElementById('address-field')

window.addEventListener("DOMContentLoaded", (event) => {


});

//<script>
/* To connect using MetaMask */
async function connect() {

    if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: "eth_requestAccounts" })
        window.web3 = new Web3(window.ethereum)
//        alert(web3.eth.getBalance)
        usernameField = document.getElementById('username-field')
        usernameField.classList.add('text-animated-username')

        addressField = document.getElementById('address-field')
        addressField.style.width = usernameField.clientWidth
        addressField.classList.add('text-animated-address')
//        addressField.innerHTML = '' + accounts[0].slice(0, 6) + "..."

        // save address to user
        $.ajax({
          url: "/user_new_address",
          type: "post",
          dataType: "json",
          contentType: "application/json; charset=UTF-8",
          data: JSON.stringify({
            "address":accounts[0]
          }),
          success: function(self) {
            connect_wallet_button.innerHTML = self.label
          },
          error: function(e) {
            console.log(e);
          }
        });

//        alert(accounts[0])
    } else {
        console.log("No wallet")
    }


}
//</script>

function checkMetaMaskInstalled() {
    if(typeof window.ethereum == 'undefined') {
        alert('not installed');
    } else {
        alert('yes you have it');
    }

}

//async function connectMetaMask() {
//    const accounts = await window.ethereum.request({method: 'eth_requestAccounts'}).then(accounts => {
//        account = accounts[0];
//        console.log(account);
//
//      });
//
//    if (!accounts) { return }
//
//    alert(accounts[0])
//}

//    function signoutMetaMask ()



//      let account;
//      ethereum.request({method: 'eth_requestAccounts'}).then(accounts => {
//        account = accounts[0];
//        console.log(account);
//
//      });
//    });
//}