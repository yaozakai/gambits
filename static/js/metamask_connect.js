var usernameField = null
var addressField = null
var connect_wallet_button = document.getElementById('connect-wallet')
connect_wallet_button.addEventListener('click', connect)


var usernameField = document.getElementById('username-field')
//var addressField = document.getElementById('address-field')
//var addressFieldSub = document.getElementById('address-field-sub')


//window.addEventListener("DOMContentLoaded", (event) => {
//
//
//});

/* To connect using MetaMask */
async function connect() {

    if (typeof window.ethereum !== 'undefined') {
        var accounts = await window.ethereum.request({ method: "wallet_requestPermissions", params: [{ eth_accounts: {} }] })
        const account_connected = accounts[0] || false;
        if (!account_connected) {

            alert_box.classList.add('show')
            return

        }
        window.web3 = new Web3(window.ethereum)
//        usernameField = document.getElementById('username-field')
//        addressField = document.getElementById('address-field')

        // save address to user
        $.ajax({
          url: "/user_new_address",
          type: "post",
          dataType: "json",
          contentType: "application/json; charset=UTF-8",
          data: JSON.stringify({
            "address":accounts[0]['caveats'][0]['value'][0]
          }),
          success: function(response) {
//            addressField.style.width = usernameField.clientWidth - 20
//            addressField.style.height = usernameField.clientHeight
//            addressFieldSub.innerHTML = response.address

//            usernameField.classList.add('text-animated-username')
//            addressField.classList.add('text-animated-address')

          },
          error: function(e) {
            console.log('user_new_address: ' + e);
          }
        });
    } else {
        console.log("No wallet")
    }
}

