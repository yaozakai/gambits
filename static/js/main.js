function isEmail(email){

	return /^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$/.test( email );
}

function snb_table_click(){
    event.stopPropagation();

    const $target = $(event.target);
    const rowDrop = $target.closest("tr").next().find("div").first()

    const row = $target.closest("td").first()

    if( rowDrop.is(":visible") ) {
        rowDrop.slideUp();
        $target.closest("tr").find("i.bi-chevron-right").css("transform","rotate(0deg)")
    } else {
        rowDrop.slideDown();
        $target.closest("tr").find("i.bi-chevron-right").css("transform","rotate(90deg)")
    }

}

function verify_sms_code(){

//    $('#login-spinner').outerHeight($('#loginbtn').outerHeight());
//    $('#login-spinner').outerWidth($('#loginbtn').outerWidth());
//    $('#login-spinner').css({
//        'display': 'inline-flex'
//    });

    const country_code = $(".iti__selected-dial-code").first()[0].textContent
    const phone = $("#mobile_code").val()

    $('#snb-sms-verify').prop('disabled', true)

    var no = [country_code, phone].join('')

    $.ajax({
        url: "/verifySMScode",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "code":$('#sms-digitfield-first').val().trim(),
            "phone":no.trim()
        }),
        success: function(self) {
            $('#snb-sms-verify').prop('disabled', false)
            if (self.error == 0){
                send_alert("snb:task:sms", "snb:task:phone:success", false, '', 'green')
                $('#snb-phone-status').addClass('bi-check-square-fill')
                $('#snb-phone-status').removeClass('bi-exclamation-square-fill')
                $('#snb-phone-status').css('color', 'green')
//                $('#span-snb-phone').remove()

                $("#sms-rowDrop").remove()
                $("#span-snb-phone").remove()
                $('#snb-row-sms').find("i.bi-chevron-right").remove()


            } else if (self.error == 1){
                send_alert("snb:task:sms", "sms:error:incorrectPin")
            } else if (self.error == 2) {
                send_alert('alert:phone', 'sms:error:phoneExists')
            } else if (self.error == 3) {
                send_alert('alert:phone', 'sms:error:incorrectPhone')
            } else if (self.error == 4) {
                send_alert('alert:phone', 'sms:error:expired')
            }
        },
        error: function(e) {
            $('#snb-sms-verify').prop('disabled', false)
            send_alert('alert:phone', 'alert:SMSserver')
        }
    });
}

function ajax_connect_twitter(){

    $.ajax({
        url: "/connect_twitter",
        type: "GET",
        success: function (data) {
            window.location.replace(data);
        },
        error: function(e) {
            send_alert('alert:phone', 'alert:SMSserver')
        }
    });


//    $.ajax({
//        url: "/connect_twitter",
//        type: "post",
//        dataType: "json",
//        contentType: "application/json; charset=UTF-8",
//        data: JSON.stringify({
//            "recipient":no
//        }),
//        success: function(self) {
//            if (self.error == 0){
//                // do nothing
//                return
//            } else if (self.error == 1) {
//                send_alert('alert:phone', 'alert:SMSserver')
//            } else if (self.error == 2) {
//                send_alert('alert:phone', 'sms:error:phoneExists')
//            }
//        },
//        error: function(e) {
//            send_alert('alert:phone', 'alert:SMSserver')
//        }
//    });
}

function send_sms(){
    var regexp = /^[\s()+-]*([0-9][\s()+-]*){6,20}$/
    const country_code = $(".iti__selected-dial-code").first()[0].textContent
    const phone = $("#mobile_code").val()

    var no = [country_code, phone].join('')

    if (!regexp.test(no) || phone.length < 6) {
        send_alert('alert:phone', 'alert:invalidPhone')
        return
    }

    $('#sms-rowDrop').slideDown()
//    $('#snb-sms-container').slideToggle()

    $('#sms-send-button').prop('disabled', true)
    $('#sms-send-button').html('<span id="countdown">60</span>')
    var n = document.getElementById("countdown")
    e = parseInt(n.innerText)
    t = setInterval((function() {
        e--
        n.innerText = e
        e <= 0 && (
            clearInterval(t),
            $('#sms-send-button').html('<i class="bi bi-send"></i>'),
            $('#sms-send-button').prop('disabled', false)
//            $target.closest("tr").find("i.bi-chevron-right").css("transform","rotate(0deg)")

//            $('.sms-digitfield').each(function () {
//                $(this).css
//            })
      )

    }), 1000)

    $.ajax({
        url: "/sendSMS",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "recipient":no
        }),
        success: function(self) {
            if (self.error == 0){
                // do nothing
                return
            } else if (self.error == 1) {
                send_alert('alert:phone', 'alert:SMSserver')
            } else if (self.error == 2) {
                send_alert('alert:phone', 'sms:error:phoneExists')
            }
        },
        error: function(e) {
            send_alert('alert:phone', 'alert:SMSserver')
        }
    });


}

function copyToClipboard(text_to_copy) {

//    var session = $('#meta-session').data()['name']
    const translations = $('#meta-translations').data()['name']


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
        $(document.body).removeClass('modal-open');
        $('.modal-backdrop').remove();

        if (self.link.toString().length > 0){
            window.open(self.link.toString());
        } else {
            send_alert('network:down', 'try again later')
        }
      },
      error: function(e) {
        $('#loadingscreenModal').modal('hide');
            $('body').removeClass('modal-open');
            $('.modal-backdrop').remove();
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
//            send_alert('reload website', '')
            reload_popup('reload:title', 'reload:msg')
            $('#notificationModal').modal({
                backdrop: 'static',
                keyboard: false
            })

//            console.log('getBalance error: ' + e);
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
//
//function includeHTML() {
//  var z, i, elmnt, file, xhttp;
//  /* Loop through a collection of all HTML elements: */
//  z = document.getElementsByTagName("*");
//  for (i = 0; i < z.length; i++) {
//    elmnt = z[i];
//    /*search for elements with a certain atrribute:*/
//    file = elmnt.getAttribute("w3-include-html");
//    if (file) {
//      /* Make an HTTP request using the attribute value as the file name: */
//      xhttp = new XMLHttpRequest();
//      xhttp.onreadystatechange = function() {
//        if (this.readyState == 4) {
//          if (this.status == 200) {elmnt.innerHTML = this.responseText;}
//          if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
//          /* Remove the attribute, and call this function once more: */
//          elmnt.removeAttribute("w3-include-html");
//          includeHTML();
//        }
//      }
//      xhttp.open("GET", file, true);
//      xhttp.send();
//      /* Exit the function: */
//      return;
//    }
//  }
//}
