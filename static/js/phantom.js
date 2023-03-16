document.getElementById("login").addEventListener("click", login);
document.getElementById("disconnect").addEventListener("click", disconnect);

// Setting up POST trigger
var params = ''
var publicKey_string = ''
var logged_in_wallet_balance = 0
var logged_in = false


function disconnect() {
    window.solana.disconnect();
    document.getElementById("login").innerHTML = '<i class="bi bi-wallet2"></i> Connect';
    document.getElementById("disconnect").style.display = "none";
    document.getElementById("balance").style.display = "none";
    document.getElementById("login").disabled = false;

    if (document.getElementById("top_bar").clientWidth < 768) {
        document.getElementById("top_bar").style.height = '64px';
        document.getElementById("myCarousel").style.marginTop = document.getElementById("top_bar").clientHeight + 'px';
//        document.getElementById("middle_bar").style.marginTop = document.getElementById("myCarousel").clientHeight + document.getElementById("top_bar").clientHeight + 'px';

        if (window.pageYOffset >= document.getElementById("myCarousel").clientHeight) {
            document.getElementById("middle_bar").style.marginTop = '-46px';
        } else {
            document.getElementById("middle_bar").style.marginTop = '42px';
        }
    }
};

async function fetchHtmlAsText(url) {
    return await (await fetch(url)).text();
}


function login() {

    const getProvider = async () => {
      if ("solana" in window) {
        await window.solana.connect(); // opens wallet to connect to
        const provider = window.solana;
        if (provider.isPhantom) {
            console.log("Is Phantom installed?  ", provider.isPhantom);
            publicKey_string = provider.publicKey.toString()
            publicKey_short = publicKey_string.substring(0, 3) + "..." + publicKey_string.slice(publicKey_string.length - 3)
            document.getElementById("login").innerHTML = '<i class="bi bi-wallet2"> ' + publicKey_short + "  </i></button>";
            document.getElementById("disconnect").style.display = "inline-block";

            console.log("Wallet Connected: " + provider.isConnected);
            if (provider.isConnected) {
                document.getElementById("balance").innerHTML = 'Getting balance...'

                const wallet = new solanaWeb3.PublicKey(provider.publicKey.toString());

                // connect to the cluster
                console.log("Connecting Cluster");
                var connection = new solanaWeb3.Connection(solanaWeb3.clusterApiUrl('devnet'), 'confirmed');

                // remember, do not use base 58 encoded key with getBalance();
                console.log("Getting Balance: " + publicKey_string);
                logged_in_wallet_balance = await connection.getBalance(provider.publicKey);

                var http = new XMLHttpRequest();
                var url = 'login';
                http.open('POST', url, true);

                //Send the proper header information along with the request
                http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

                document.getElementById("login").disabled = true;
//                http.send('balance=' + logged_in_wallet_balance + '&walletID=' + publicKey_string);

                const response = await fetch(url, {
                    method: 'POST', // *GET, POST, PUT, DELETE, etc.
                    headers: {
//                      'Content-Type': 'application/json'
                       'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: JSON.stringify('balance=' + logged_in_wallet_balance + '&walletID=' + publicKey_string) // body data type must match "Content-Type" header
                  });

                myCarousel_window = document.getElementById("myCarousel")

                document.getElementById("balance").innerHTML = 'Balance: ' + (logged_in_wallet_balance / 1000000000).toFixed(4) + " " + await fetchHtmlAsText("static/deposit_balance.html");
                document.getElementById("balance").style.display = 'inline-block';
                if (document.getElementById("top_bar").clientWidth < 768) {
                    document.getElementById("top_bar").style.height = '110px';
                    myCarousel_window.style.marginTop = document.getElementById("top_bar").clientHeight + 'px';

                    document.getElementById("middle_bar").style.marginTop = '-8px';
                    document.getElementById("main_section").style.marginTop = '62px';

                }
                console.log(logged_in_wallet_balance);


            }

          return provider;
        }
        window.open("https://phantom.app/", "_blank");
      } else {
        window.open("https://phantom.app/", "_blank");
      }
    };

    console.log("Logging in...");

    getProvider().then(provider => {
        console.log('key', provider.publicKey.toString())
    })
    .catch(function(error){
    console.log(error)
    });



};
