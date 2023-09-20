  function userDetailFormatter(index, row) {
    var arr = ['snb_phone', 'snb_twitter']
    var newArr = arr.map(function(val, index){

      // printing element
      console.log("key : ",index, "value : ",val*val);
    })

    var html = []
    html.push ('<tr>')
    $.each(row, function (key, value) {
        arr.map(function(val, index){
            if( val == key ){
                html.push('<th>' + key + '</th>')
            }
        })
    })
    html.push ('</tr>')
    html.push ('<tr>')
    $.each(row, function (key, value) {
        arr.map(function(val, index){
            if( val == key ){
                html.push('<td>' + value + '</td>')
            }
        })
    })
    html.push ('</tr>')

    return html.join('')
  }

  function initTable() {
    const txn_data = $('#meta-user_data').data()['name'].replaceAll(`'`, `"`)

    $('#users_table').bootstrapTable('destroy').bootstrapTable({
      data: JSON.parse(txn_data),
      height: 750,
      columns: [
        [{
          title: 'User ID',
          field: 'user_id',
          align: 'center',
          valign: 'middle',
          sortable: true
        }, {
          title: 'Created',
          field: 'created',
          align: 'center',
          valign: 'middle',
          sortable: true,
        }, {
          field: 'username',
          title: 'Username',
          sortable: true,
          align: 'center'
        }, {
          field: 'email',
          title: 'Email',
          sortable: true,
          align: 'center'
        }, {
          field: 'referral',
          title: 'Referral',
          sortable: true,
          align: 'center'
        }, {
          field: 'balance_usdt',
          title: 'Balance',
          sortable: true,
          align: 'center',
        }, {
          field: 'logged_in',
          title: 'logged_in',
          sortable: true,
          align: 'center',
        }, {
          field: 'active',
          sortable: true,
          title: 'Active',
          align: 'center',
        }]
      ]
    }).bootstrapTable('sortBy', {
        field: 'status',
        sortOrder: 'desc'
    })



  }

  $(function() {
    initTable()

//    $('#locale').change(initTable)
  })