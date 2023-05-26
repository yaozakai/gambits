//$(document).ready(function(){
window.addEventListener("DOMContentLoaded", (event) => {



//    formatted = formatted.replace(/'/g, '"')
//    formatted = formatted.replace(/#/g, "'")



//    console.log('lang: ' + lang)
});

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

async function send_alert(title, msg, native=false, appendix='') {
    var alert_box = document.getElementById('alert-box')
    var alert_title = document.getElementById('alert-title')
    var alert_message = document.getElementById('alert-message')

    var translations = $('#meta-translations').data()['name']
    var lang = $('#meta-lang').data()['name']

    alert_box.classList.remove('show')

    $('#deposit-spinner').hide();
    if (native) {
        alert_title.innerHTML = title
        alert_message.innerHTML = msg + appendix
        alert_box.classList.add('show')
        return
    } else {
        alert_title.innerHTML = translations[title][lang]
        alert_message.innerHTML = translations[msg][lang] + appendix
        alert_box.classList.add('show')


//        $.ajax({
//          url: "/translate_alert",
//          type: "post",
//          dataType: "json",
//          contentType: "application/json; charset=UTF-8",
//          data: JSON.stringify({
//            "title":title,
//            "msg":msg
//          }),
//          success: function(response) {
//            if (msg == 'success:txnSent') {
//                alert_title.innerHTML = response.title + '...<div class="spinner-border show" style="height: 15px;width: 15px;"></div>'
//            } else {
//                alert_title.innerHTML = response.title
//            }
//            alert_message.innerHTML = response.msg + msg_native
//            alert_box.classList.add('show')
//            return
//          },
//          error: function(e) {
//            console.log('translate_alert: ' + e);
//          }
//        });
    }
}

function get_balance(){
    $.ajax({
        url: "/getBalance",
        type: "post",
        success: function(balances) {
            balance_field_eth.innerHTML = '<span class="crypto-symbol">ETH</span> ' + balances['eth']
            balance_field_usdt.innerHTML = '<span class="crypto-symbol">USDT</span> ' + balances['usdt']
            withdraw_balance.innerHTML = balances['usdt']
<!--                    balance_field_eth.value = balances['eth'];-->
<!--                    balance_field_usdt.value = balances['usdt'];-->
        },
        error: function(e) {
            console.log('getBalance: ' + e);
        }
    });
}

function txnHistory(){
    const selectElement = document.getElementById('reportDate');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }
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
        "txHash":txHash,
        "chain":chain,
        "currency": currency,
        "amount": amount,
        "fromAddress": fromAddress,
        "mode": mode,
      }),
      success: function(response) {
        alert_title.innerHTML = response.notification_title

        if (response.alert_type == 'success:txnSuccess') {
            alert_message.innerHTML = response.amount + ' <span style="font-size: small;">' + response.currency.toUpperCase() + '</span> ' + response.notification
            alert_box.classList.remove('alert-danger')
            if (mode == "post"){
                alert_box.classList.add('alert-warning')
                $("#row-" + txHash).html('Complete')
                $("#row-" + txHash).css('color', 'green')
            } else {
                alert_box.classList.add('alert-success')
            }
            alert_box.classList.add('show')

            return true
        } else if (response.alert_type == 'alert:timeout') {
            alert_message.innerHTML = response.notification
            alert_box.classList.add('alert-danger')
            alert_box.classList.remove('alert-success')
            alert_box.classList.add('show')
            return false
        }

      },
      error: function(e) {
        console.log('verify_txhash error: ' + e);
      }
    });

}