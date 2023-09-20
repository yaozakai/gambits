//if (typeof iti !== 'undefined'){

let current_page = 'gallery'

function nav_jump(item) {
    var header_tag = $(item).attr("id")
    header_tag = header_tag.slice(4, header_tag.length)

    if (current_page == 'gallery'){
        document.getElementById('header-' + header_tag).scrollIntoView();
    } else {
        go_to_gallery('header-' + header_tag)
    }


}

function go_to_gallery(id) {
    $('#loadingscreenModal').modal('show');


    current_page = 'gallery'
    console.log('page:: ' + current_page)
//    $("#back-to-games").hide()
    $.ajax({
        url: "/gallery",
        type: "post",
        success: function(self) {
            close_modal()

            $("#main_section").html(self);
            document.getElementById(id).scrollIntoView()
        },
        error: function(e) {
            close_modal()
            console.log('gallery: ' + e);

            send_alert('network:down', 'try again later')

        }
    });
}

function go_to_pendingWithdraw(){
    $('#loadingscreenModal').modal('show');
    if (current_page == 'gallery'){
        navbar_clear()
    }

    current_page = 'pendingWithdraw'
    console.log('page:: ' + current_page)
    const selectElement = document.getElementById('reportDate');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }

    $.ajax({
        url: "/pendingWithdraw",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            close_modal()
            $("#main_section").html(self.div_render);
        },
        error: function(e) {
            close_modal()

            console.log('txnHistory: ' + e);
            send_alert('network:down', 'try again later')

//            return false
        }
    });
    return true
}

function go_to_searchPlayer(){
    $('#loadingscreenModal').modal('show');
    if (current_page == 'gallery'){
        navbar_clear()
    }
    current_page = 'searchPlayer'
    console.log('page:: ' + current_page)
//    $("#back-to-games").show()

    $.ajax({
        url: "/search_page",
        type: "post",
        success: function(self) {
            close_modal()
            $("#main_section").html(self.div_render)
        },
        error: function(e) {
            console.log('searchPlayer: ' + e);
            send_alert('network:down', 'try again later')
        }
    });
}

function go_to_gameHistory(){
    $('#loadingscreenModal').modal('show');
    if (current_page == 'gallery'){
        navbar_clear()
    }

    current_page = 'gameHistory'
    console.log('page:: ' + current_page)
    const selectElement = document.getElementById('reportDateGameHistory');
    let reportDate = ''
    if (selectElement) {
        reportDate = selectElement.value
    }
//    $("#back-to-games").show()

    $.ajax({
        url: "/gameHistory",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            close_modal()

            $("#main_section").html(self.div_render);
        },
        error: function(e) {
            close_modal()

            console.log('gameHistory error: ' + e);
        }
    });

}

function go_to_txnHistory(reportDate=''){
    $('#loadingscreenModal').modal('show');
    if (current_page == 'gallery'){
        navbar_clear()
    }

    current_page = 'txnHistory'
    console.log('page:: ' + current_page)

//    $("#back-to-games").show()

    $.ajax({
        url: "/txnHistory",
        type: "post",
        dataType: "json",
        contentType: "application/json; charset=UTF-8",
        data: JSON.stringify({
            "reportDate":reportDate
        }),
        success: function(self) {
            close_modal()

            $("#main_section").html(self.div_render);

        },
        error: function(e) {
            close_modal()

            console.log('txnHistory error: ' + e);
//            return false
        }
    });

    return true
}

function close_modal() {
    $('#loadingscreenModal').modal('hide');
//    $('.modal-backdrop').remove();
    var thisClass = $(this).attr("modal-backdrop");
    $('div.' + thisClass).remove();

//    $( "#loading-modal-close" ).trigger( "click" );
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

function reload_popup(title, msg){
    $('#modalNotificationTitle').html(title)
    $('#modalNotificationMsg').html(msg)
    $('#notificationModal').modal('show', {backdrop: 'static', keyboard: false})
}

async function send_alert(title, msg, native=false, appendix='', color='red', symbol='') {
    var alert_box = document.getElementById('alert-box')
    var alert_title = document.getElementById('alert-title')
    var alert_message = document.getElementById('alert-message')

    var translations = $('#meta-translations').data()['name']
    var lang = $('#meta-lang').data()['name']

    $('alert-box').toggle()

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

    setTimeout(function(){
        alert_box.classList.remove('show')
    }, 5000);
}

function navbar_clear(){
//    const curr_active = document.getElementsByClassName('navbar-fixed a').removeClass('active');
    $(".navbar-fixed a").removeClass('active')
}