$(document).ready(function(){
    const notify = $('#meta-notify').data()['name']
//    const translations = $('#meta-translations').data()['name']
//    const lang = $('#meta-lang').data()['name']

    if (notify == 'oauth') {
        reload_popup('snb:subtask:twt', 'snb:subtask:twt:success')
    }
})
