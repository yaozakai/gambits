var usernameField = null
var addressField = null
var connect_wallet_button = document.getElementById('connect-wallet')
    connect_wallet_button.addEventListener('click', connect)


var usernameField = document.getElementById('username-field')
var addressField = document.getElementById('address-field')
var alert_box = document.getElementById('alert-box')

window.addEventListener("DOMContentLoaded", (event) => {


});

//<script>
/* To connect using MetaMask */
async function connect() {

    if (typeof window.ethereum !== 'undefined') {
//        var accounts = async () =>  await window.ethereum.request({ method: "eth_requestAccounts" })
        var accounts = await window.ethereum.request({ method: "wallet_requestPermissions", params: [{ eth_accounts: {} }] })
        const account_connected = accounts[0] || false;
        if (!account_connected) {

            alert_box.classList.add('show')
            return

        }
        window.web3 = new Web3(window.ethereum)
        usernameField = document.getElementById('username-field')
//        usernameField.classList.add('text-animated-username')

        addressField = document.getElementById('address-field')
//        addressField.style.width = usernameField.clientWidth
//        addressField.classList.add('text-animated-address')

        // save address to user
        $.ajax({
          url: "/user_new_address",
          type: "post",
          dataType: "json",
          contentType: "application/json; charset=UTF-8",
          data: JSON.stringify({
            "address":accounts[0]['caveats'][0]['value'][0]
          }),
          success: function(self) {
            addressField.innerHTML = session['publicAddress']
            addressField.style.width = user_field.clientWidth - 20
            addressField.style.height = user_field.clientHeight
            addressField.innerHTML = "{{ current_user.publicAddress }}"

            usernameField.classList.add('text-animated-username')
            addressField.classList.add('text-animated-address')

            alert_box.classList.add('show')

            alert_title = document.getElementById('alert-title')
            alert_message = document.getElementById('alert-message')

            alert_title.innerHTML = self.address_set_title
            alert_message.innerHTML = self.address_set_message
          },
          error: function(e) {
            console.log(e);
          }
        });
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