//$('.launch').on('click', function(){
//    event.preventDefault();

function copyToClipboard(text_to_copy) {

//    var session = $('#meta-session').data()['name']
    var translations = $('#meta-translations').data()['name']


//    var $temp = ;
    $("#value-clipboard").val(text_to_copy)
//    $("body").append($temp);
//    $("#value-clipboard").select();
    let original_width = $("#copy-button").width()
    $("#copy-button").html(translations['done'][lang] + '!')
    $("#copy-button").width(original_width);


    $("#value-clipboard").select()
    if( document.execCommand("copy") ){
        console.log('copied');
      }
//    $temp.remove();
}


function launch_game() {
    $.ajax({
      url: "/launch",
      type: "post",
      dataType: "json",
      contentType: "application/json; charset=UTF-8",
      data: JSON.stringify({
        "id":event.target.id
      }),
      success: function(self) {
        $('#loadingscreenModal').modal('hide');
        if (self.link.toString().length > 0){
            window.open(self.link.toString());
        } else {
            send_alert('network:down', 'try again later')
        }
      },
      error: function(e) {

      }
    });
}

function go_to_gallery() {

    current_page = 'gallery'
    console.log('page:: ' + current_page)
    $("#back-to-games").hide()
    $.ajax({
        url: "/gallery",
        type: "post",
        success: function(self) {
            $("#main_section").html(self);
        },
        error: function(e) {
            console.log('getBalance: ' + e);
        }
    });
}

function go_to_searchPlayer(){

    current_page = 'searchPlayer'
    console.log('page:: ' + current_page)
    $("#back-to-games").show()

    $.ajax({
        url: "/search_page",
        type: "post",
        success: function(self) {
            $("#main_section").html(self.render);
        },
        error: function(e) {
            console.log('/search_page: ' + e);
        }
    });
}

function go_to_gameHistory(){
    current_page = 'gameHistory'
    console.log('page:: ' + current_page)
    const selectElement = document.getElementById('reportDateGameHistory');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }
    $("#back-to-games").show()

    $.ajax({
        url: "/gameHistory",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            $("#main_section").html(self.render);
        },
        error: function(e) {
            console.log('gameHistory error: ' + e);
        }
    });
}

function go_to_pendingWithdraw(){
    current_page = 'pendingWithdraw'
    console.log('page:: ' + current_page)
    const selectElement = document.getElementById('reportDate');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }
    $("#back-to-games").show()

    $.ajax({
        url: "/pendingWithdraw",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            $("#main_section").html(self.render);
//            return true
        },
        error: function(e) {
            console.log('txnHistory: ' + e);
//            return false
        }
    });
    return true
}

function go_to_txnHistory(reportDate=''){
    current_page = 'txnHistory'
    console.log('page:: ' + current_page)

//    $('#alert-box').removeClass('show')

//    const selectElement = document.getElementById('reportDate');
//    let reportDate = ''
//    if (selectElement && reportDate.length == 0) {
//        reportDate = selectElement.value
//    } else if (reportDate == 'today'){
//        reportDate = ''
//    }
    $("#back-to-games").show()

    $.ajax({
        url: "/txnHistory",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            $("#main_section").html(self.render);
//            return true
        },
        error: function(e) {
            console.log('txnHistory: ' + e);
//            return false
        }
    });
    return true
}

function waitForElm(selector) {
    return new Promise(resolve => {
        if (document.querySelector(selector)) {
            return resolve(document.querySelector(selector));
        }

        const observer = new MutationObserver(mutations => {
            if (document.querySelector(selector)) {
                resolve(document.querySelector(selector));
                observer.disconnect();
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    });
}



function generate_table_txnHistory(results) {
    if (typeof results == 'undefined') {
        htmloutput = "<div class=\"green-text-outline\">No data</div>";
    } else {
        for (let i = 0; i < results.length; i++) {
            htmloutput = htmloutput + "<tr>";
            htmloutput = htmloutput + "<td>" + results[i]["endroundtime"].substring(11, 19) + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["status"] + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["gametype"] + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["gamecode"] + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["round"] + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["bet"] + "</td>";
            htmloutput = htmloutput + "<td>" + results[i]["win"] + "</td>";
//<!--                    htmloutput = htmloutput + "<td>" + results[i]["validbet"] + "</td>";-->
//<!--                            htmloutput = htmloutput + "<td>" + results[i]["jackpot"] + "</td>";-->
//<!--                            htmloutput = htmloutput + "<td>" + results[i]["jackpotcontribution"] + "</td>";-->
            htmloutput = htmloutput + "<td>" + results[i]["rake"] + "</td>";
//<!--                            htmloutput = htmloutput + "<td>" + results[i]["roomfee"] + "</td>";-->
                    htmloutput = htmloutput + "</tr><tr><td colspan=\"12\" style=\"padding: 0px;\"><div class=\"rowDrop\">Detail:" + results[i]["detail"] + "<br>Result:" + results[i]["gameresult"] + "</div></td></tr>";
        };
    }
    document.getElementById("results").innerHTML = htmloutput;
}

function notification_popup(title, msg){
    var translations = $('#meta-translations').data()['name']
    var lang = $('#meta-lang').data()['name']

    $('#modalNotificationTitle').html(translations[title][lang]);
    $('#modalNotificationMsg').html(translations[msg][lang]);
    $('#notificationModal').modal('show');
}

function notification_popup_hide() {
    $('#notificationModal').modal('hide');
}

async function send_alert(title, msg, native=false, appendix='', color='red', symbol='') {
    var alert_box = document.getElementById('alert-box')
    var alert_title = document.getElementById('alert-title')
    var alert_message = document.getElementById('alert-message')

    var translations = $('#meta-translations').data()['name']
    var lang = $('#meta-lang').data()['name']

    if (alert_box.classList.contains('show')) {
        alert_box.classList.remove('show')
    }

    if (color == 'red'){
        alert_box.classList.remove('alert-info') // blue
        alert_box.classList.remove('alert-warning') // yellow
        alert_box.classList.add('alert-danger') // red
        alert_box.classList.remove('alert-success') // green
    } else if (color == 'blue'){
        alert_box.classList.add('alert-info') // blue
        alert_box.classList.remove('alert-warning') // yellow
        alert_box.classList.remove('alert-danger') // red
        alert_box.classList.remove('alert-success') // green
    } else if (color == 'yellow'){
        alert_box.classList.remove('alert-info') // blue
        alert_box.classList.add('alert-warning') // yellow
        alert_box.classList.remove('alert-danger') // red
        alert_box.classList.remove('alert-success') // green
    } else if (color == 'green'){
        alert_box.classList.remove('alert-info') // blue
        alert_box.classList.remove('alert-warning') // yellow
        alert_box.classList.remove('alert-danger') // red
        alert_box.classList.add('alert-success') // green
    }

    if (native) {
        alert_title.innerHTML = title
        alert_message.innerHTML = msg + ' ' + appendix
    } else {
        if (title.length > 0){
            alert_title.innerHTML = translations[title][lang]
        } else {
            alert_title.innerHTML = ''
        }
        if (msg.length > 0){
            alert_message.innerHTML = translations[msg][lang] + ' ' + appendix
        } else {
            alert_message.innerHTML = appendix
        }
    }

    if (alert_box.classList.contains('show')) {
        setTimeout(function(){
            alert_box.classList.add('show')
        }, 1000);
    } else {
        alert_box.classList.add('show')
    }
}


function get_balance(){
    var balance_field_usdt = document.getElementById("balance_usdt");
    var withdraw_balance = document.getElementById("withdraw-balance");

    $.ajax({
        url: "/getBalance",
        type: "post",
        success: function(balances) {
//            balance_field_eth.innerHTML = '<span class="crypto-symbol">ETH</span> ' + balances['eth']
//            balance_field_usdt.innerHTML = balances['usdt'] + ' <span class="crypto-symbol">USDT</span>'
//            withdraw_balance.innerHTML = balances['usdt']
//            $('#deposit-display-amount').html(balances['usdt'] + ' USDT @ ERC20')
            set_balance_UI(balances['usdt'])

        },
        error: function(e) {
            send_alert('reload website', '')
            console.log('getBalance error: ' + e);
        }
    });
}

function set_balance_UI(balance){
    $('#balance_usdt').html(balance + ' <span class="crypto-symbol">USDT</span>')
    $('#withdraw-balance').html(balance)

}



function verify_txhash(mode, txHash, chain, currency, amount, fromAddress) {
    var alert_box = document.getElementById('alert-box')
    var alert_title = document.getElementById('alert-title')
    var alert_message = document.getElementById('alert-message')

    $.ajax({
      url: "/verify_transaction",
      type: "post",
      dataType: "json",
      contentType: "application/json; charset=UTF-8",
      data: JSON.stringify({
        "mode": mode,
        "txHash":txHash,
        "chain":chain,
        "currency": currency,
        "amount": amount,
        "fromAddress": fromAddress,
      }),
      success: function(response) {
      // response is a TxnEntry object
//        let appendix = ' ' + amount + ' USDT'

        if (mode == "reconcile"){
            const reconcile_id = fromAddress

            $("#reconcile-" + reconcile_id).prop('disabled', true)
            $("#reconcile-" + reconcile_id).html("Done")
            $("#reconcile-" + reconcile_id).css('color', 'red')
//            $("#reconcile_id-" + reconcile_id).html('<a href="https://etherscan.io/tx/' + response.txHash + ' target="_blank">')
            $("#reconcile_id-" + reconcile_id).html('<a href="https://goerli.etherscan.io/tx/' + response.txHash + ' target="_blank"><i class="bi bi-link"></i></a>')
            $("#reconcile_status-" + reconcile_id).html("Complete")
            $("#reconcile_status-" + reconcile_id).css('color', 'red')

            alert_box.classList.remove('show')


            return true
        } else if (response.alert_type == 'success:txnSuccess') {
            // update table regardless if shown
            $("#row-" + txHash).html('Complete')
            $("#row-" + txHash).css('color', 'green')

            // send alert popup
            let msg = response.amount + ' <span style="font-size: small;">' + response.currency.toUpperCase() + '</span> ' + translations['success:txnSuccess'][lang]
            send_alert('txn:complete', '', false, msg, 'blue')

            // update balance across UI
            set_balance_UI(response.balance)

            return true

        } else if (response.alert_type == 'alert:timeout') {
            if (mode == "reverify"){
                $("#row-" + txHash).html('Failed <button onclick="reverify("row-" + txHash + "," + txHash + "," + chain + "," + currency + "," + amount + "," + fromAddress + "," + status)" class="btn btn-link reverify-button" data-bs-toggle="tooltip" data-bs-placement="right" title="{{ translations["button:reverify"][session["lang"]] }}"><i class="bi bi-arrow-clockwise"></i></button>')
                $("#row-" + txHash).css('color', 'green')
            }
            send_alert('failed:verify', 'alert:timeout', false, '', 'red')
            return false
        }
      },
      error: function(e) {
        console.log('verify_txhash error: ' + e);
//        send_alert('failed:verify', e, false, '', 'red')

        return false
      }
    });
}

function includeHTML() {
  var z, i, elmnt, file, xhttp;
  /* Loop through a collection of all HTML elements: */
  z = document.getElementsByTagName("*");
  for (i = 0; i < z.length; i++) {
    elmnt = z[i];
    /*search for elements with a certain atrribute:*/
    file = elmnt.getAttribute("w3-include-html");
    if (file) {
      /* Make an HTTP request using the attribute value as the file name: */
      xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
          if (this.status == 200) {elmnt.innerHTML = this.responseText;}
          if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
          /* Remove the attribute, and call this function once more: */
          elmnt.removeAttribute("w3-include-html");
          includeHTML();
        }
      }
      xhttp.open("GET", file, true);
      xhttp.send();
      /* Exit the function: */
      return;
    }
  }
}
