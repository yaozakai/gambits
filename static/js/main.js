function isEmail(email){

	return /^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])*\x22))*\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])*\x5d))*$/.test( email );
}

//var session = $('#meta-session').data()['name']
//
//if( session.is)
var loopCount = 10
// socials countdown
var mainLoopId = setInterval(function(){
    $('#socials-counter').html(loopCount.toString())
    loopCount--
    if( loopCount < 0 ){
        kill_socials()
    }
}, 1000)

function kill_socials(){
    clearInterval(mainLoopId)
    $('#socials-container').slideUp()
}

const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

function verify_sms_code(){

    const country_code = $(".iti__selected-dial-code").first()[0].textContent
    const phone = $("#mobile_code").val()

    $('#snb-sms-verify').prop('disabled', true)

    var no = [country_code, phone].join('')

    $.ajax({
        url: "/verifySMSOTP",
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
                $('#snb-phone-status').removeClass('bi-x-square-fill')
                $('#snb-phone-status').css('color', 'green')
                $("#flush-collapse1").remove()
//                $("#span-snb-phone").remove()
//                $('#snb-row-sms').find("i.bi-chevron-right").remove()


            } else if (self.error == 1){
                send_alert("snb:task:sms", "sms:error:incorrectPin")
            } else if (self.error == 2) {
                send_alert('alert:phone', 'sms:error:expired')
            }
        },
        error: function(e) {
            $('#snb-sms-verify').prop('disabled', false)
            send_alert('alert:phone', 'alert:SMSserver')
        }
    });
}

function ajax_submit_tweet_url(){
    $('#loadingscreenModal').modal('show')

    $.ajax({
        url: "/submit_tweet_url",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "url":$('#tweet-url').val().trim()
        }),
        success: function (response) {
            $('#loadingscreenModal').modal('hide')

            $('#snb-twitter-status').addClass('bi-exclamation-square-fill')
            $('#snb-twitter-status').removeClass('bi-x-square-fill')
            $('#snb-twitter-status').css('color', 'yellow')
//            $('#span-snb-twitter').remove()
//            $('#snb-row-twitter').find("i.bi-chevron-right").remove()

            send_alert('snb:subtask:twt', 'snb:subtask:twt:success', color='green')
        },
        error: function(e) {
            $('#loadingscreenModal').modal('hide')
            send_alert('snb:subtask:twt', 'try again later')
        }
    })
}



function ajax_connect_twitter(){

    $.ajax({
        url: "/submit_tweet_url",
        type: "GET",
        success: function (response) {
//            window.location.replace(response);
            location.href = response;
        },
        error: function(e) {
            $('#loadingscreenModal').modal('hide')
            send_alert('snb:subtask:twt', 'try again later')
        }
    });
}


function ajax_oauth_discord(){
    $.ajax({
        url: "/oauth/discord",
        type: "GET",
        success: function (response) {
//            window.location.replace(response);
            location.href = response;
        },
        error: function(e) {
            $('#loadingscreenModal').modal('hide')
            send_alert('snb:subtask:twt', 'try again later')
        }
    });
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

    $.ajax({
        url: "/send_SMS",
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

    $('#sms-rowDrop').slideDown()
//    $('#snb-sms-container').slideToggle()

    $('#sms-send-button').prop('disabled', true)
    $('#sms-send-button').html('<span id="countdown">60</span>')
    var countdown = document.getElementById("countdown")
    var theCount = parseInt(countdown.innerText)
    t = setInterval((function() {
        theCount--
        countdown.innerText = theCount
        theCount <= 0 && (
            clearInterval(t),
            $('#sms-send-button').html('<i class="bi bi-send"></i>'),
            $('#sms-send-button').prop('disabled', false)
      )
    }), 1000)
}

//function lang_change(item) {
//
//    $.ajax({
//            url: "/lang/" + $(item).attr("id").split('-')[1],
//            type: "GET",
//            success: function(response) {
//                document.write(response)
//            },
//            error: function(e) {
//                send_alert('reload:title', 'reload:msg')
//            }
//        });
//
//}

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
//            $('#notificationModal').modal({
//                backdrop: 'static',
//                keyboard: false
//            })

//            console.log('getBalance error: ' + e);
        }
    });
}

function set_balance_UI(balance){
    $('#balance_usdt').html(balance + ' <span class="crypto-symbol">USDT</span>')
    $('#withdraw-balance').html(balance)

}

function svrConfirmTweet(user_id) {
    $('#loadingscreenModal').modal('show')

    $.ajax({
      url: "/confirm_tweet",
      type: "post",
      dataType: "json",
      contentType: "application/json; charset=UTF-8",
      data: JSON.stringify({
        "user_id": user_id
      }),
      success: function(response) {
        $('#loadingscreenModal').modal('hide')
        $('#confirmTweet-' + response.user_id).html('Done')
        $('#confirmTweet-' + response.user_id).addClass('disabled')
      },
      error: function(e) {
        console.log('verify_txhash error: ' + e);
//        send_alert('failed:verify', e, false, '', 'red')

        return false
      }
    });

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

            $("#reconcile-" + reconcile_id).prop('disabled', true).html("Done!").addClass('btn-primary').removeClass('btn-info')
            $("#can-reconcile" + reconcile_id).hide()

            $("#reconcile-" + reconcile_id).parent().parent().children().each(function () {
                if( $(this)[0].textContent == 'Pending' ){
                    $(this)[0].textContent = 'Complete'
                }
            })
            $("#reconcile-" + reconcile_id).parent().parent().children().css('background', 'var(--lightPurp)')
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
