
//import MetaMaskSDK from '../../@metamask/sdk';
//
//const MMSDK = new MetaMaskSDK()
//
//const ethereum = MMSDK.getProvider() // You can also access via window.ethereum
//
//ethereum.request({method: 'eth_requestAccounts'})
document.getElementById('connect-wallet').addEventListener('click', connect)

//<script>
/* To connect using MetaMask */
async function connect() {

    if (window.ethereum) {
        const accounts = await window.ethereum.request({ method: "eth_requestAccounts" })
        window.web3 = new Web3(window.ethereum)
//        alert(web3.eth.getBalance)
        alert(accounts[0])
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