var usernameField = null
var addressField = null
var connect_wallet_button = document.getElementById('connect-wallet')
connect_wallet_button.addEventListener('click', connect)
document.getElementById('money-send').addEventListener('click', sendMoney)


var usernameField = document.getElementById('username-field')
var addressField = document.getElementById('address-field')
var addressFieldSub = document.getElementById('address-field-sub')
var alert_box = document.getElementById('alert-box')
var alert_title = document.getElementById('alert-title')
var alert_message = document.getElementById('alert-message')

window.addEventListener("DOMContentLoaded", (event) => {


});

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
            addressField.style.width = usernameField.clientWidth - 20
            addressField.style.height = usernameField.clientHeight
            addressFieldSub.innerHTML = response.address

            usernameField.classList.add('text-animated-username')
            addressField.classList.add('text-animated-address')


            alert_title.innerHTML = response.address_set_title
            alert_message.innerHTML = response.address_set_message
            alert_box.classList.add('show')
          },
          error: function(e) {
            console.log(e);
          }
        });
    } else {
        console.log("No wallet")
    }
}

async function sendMoney() {
    // Send Ethereum to an address
    var accounts = await window.ethereum.request({ method: "wallet_requestPermissions", params: [{ eth_accounts: {} }] })
    const account_connected = accounts[0] || false;
    if (!account_connected) {
        alert_box.classList.add('show')
        return
    }
//    window.web3 = new Web3(window.ethereum)


//    deposit_amount = document.getElementById('deposit-amount')
    deposit_amount = parseFloat(document.getElementById('deposit-amount').value)

    window.ethereum.request({
      method: 'eth_sendTransaction',
      params: [
        {
          from: accounts[0]['caveats'][0]['value'][0], // The user's active address.
          to: '0x6E38B4dc98854E5CA41db2F9AfaCE7F7656ab33B',
          value: '0x' + (1000000000000000000 * deposit_amount).toString(16),
          gasPrice: '0x09184e72a000', // Customizable by the user during MetaMask confirmation.
          gas: '0x2710', // Customizable by the user during MetaMask confirmation.
        },
      ],
    })
    .then((txHash) => console.log(txHash))
    .catch((error) => console.error(error));
//    });

//    if(typeof window.ethereum == 'undefined') {
//        alert('not installed');
//    } else {
//        alert('yes you have it');
//    }

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