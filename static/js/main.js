//window.addEventListener("DOMContentLoaded", (event) => {



function go_to_gallery() {
//    $("#back-to-games").hide()
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
<!--                    htmloutput = htmloutput + "<td>" + results[i]["validbet"] + "</td>";-->
<!--                            htmloutput = htmloutput + "<td>" + results[i]["jackpot"] + "</td>";-->
<!--                            htmloutput = htmloutput + "<td>" + results[i]["jackpotcontribution"] + "</td>";-->
            htmloutput = htmloutput + "<td>" + results[i]["rake"] + "</td>";
<!--                            htmloutput = htmloutput + "<td>" + results[i]["roomfee"] + "</td>";-->
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
        alert_message.innerHTML = msg + appendix
        return
    } else {
        if (title.length > 0){
            alert_title.innerHTML = translations[title][lang]
        } else {
            alert_title.innerHTML = ''
        }
        if (msg.length > 0){
            alert_message.innerHTML = translations[msg][lang] + appendix
        } else {
            alert_message.innerHTML = appendix
        }
    }

    if (alert_box.classList.contains('show')) {
        alert_box.classList.remove('show')
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
            balance_field_usdt.innerHTML = '<span class="crypto-symbol">USDT</span> ' + balances['usdt']
            withdraw_balance.innerHTML = balances['usdt']
            $('#deposit-display-amount').html(balances['usdt'] + ' USDT @ ERC20')

        },
        error: function(e) {
            console.log('/getBalance: ' + e);
        }
    });
}

function searchPlayer(){
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

function gameHistory(){
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

function pendingWithdraw(){
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

function txnHistory(){
    const selectElement = document.getElementById('reportDate');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }
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

function verify_txhash(mode, txHash, chain, currency, amount, fromAddress, reconcile_id='') {
    var alert_box = document.getElementById('alert-box')
    var alert_title = document.getElementById('alert-title')
    var alert_message = document.getElementById('alert-message')

    $.ajax({
      url: "/verify_transaction",
      type: "post",
      dataType: "json",
      contentType: "application/json; charset=UTF-8",
      data: JSON.stringify({
        "txHash":txHash,
        "chain":chain,
        "currency": currency,
        "amount": amount,
        "fromAddress": fromAddress,
        "mode": mode,
        "reconcile_id": reconcile_id
      }),
      success: function(response) {
        let appendix = ' ' + amount + ' USDT'

        if (response.alert_type == 'success:txnSuccess') {
            if (mode == "post"){
//                $("#row-" + txHash).html('Complete')
//                $("#row-" + txHash).css('color', 'green')
            } else if (mode == "reconcile"){
                $("#" + amount + "-" + fromAddress).prop('disabled', true)
                $("#reconcile:" + reconcile_id).html(response.reconciled_txHash)
            }

            let msg = response.amount + ' <span style="font-size: small;">' + response.currency.toUpperCase() + '</span> ' + translations['success:txnSuccess'][lang]
            send_alert('txn:complete', '', false, msg, 'blue')
            return true

        } else if (response.alert_type == 'alert:timeout') {
            send_alert('success:waiting', 'success:txnSuccess', false, '', 'red')
            return false
        }
      },
      error: function(e) {
        console.log('verify_txhash error: ' + e);
        return false
      }
    });
}