  function detailFormatter(index, row) {
    var html = []
    $.each(row, function (key, value) {
      html.push('<p><b>' + key + ':</b> ' + value + '</p>')
    })

    return html.join('')
  }

  function operateFormatter(value, row, index) {
    return [
      '<a class="like" href="javascript:void(0)" title="Like">',
      '<i class="fa fa-heart"></i>',
      '</a>  ',
      '<a class="remove" href="javascript:void(0)" title="Remove">',
      '<i class="fa fa-trash"></i>',
      '</a>'
    ].join('')
  }

  function etherscanlinkFormatter(data) {
//    return '<a href="https://etherscan.io/address/' + data + ' target="_blank">' + data.slice(0, 6) + '..' + data.slice(-3) + '</a>'
    return '<a href="https://etherscan.io/address/' + data + '" target="_blank">' + data.slice(0, 6) + '..' + data.slice(-3) + '</a>'
  }

  function URLformatter(data) {
      if( data != 'None' ){
        return '<a href="' + data + '" target="_blank">' + data.slice(8, 14) + '..' + data.slice(-3) + '</a>'
      } else {
        return 'Not yet'
      }
  }

  function markTweetConfirmed(value, row, index) {
    if( row.snb_twitter != 'None'  ){
        return 'Done'
    } else if( row.snb_twitter_url != 'None' ){
        return [
            '<button onclick="svrConfirmTweet(\'' + row.user_id + '\');" id="confirmTweet-' + row.user_id + '" class="btn btn-info reconcile-button" data-bs-toggle="tooltip" data-bs-placement="right">Do it!</button>',
        ].join('')
    } else {
        return '····'
    }
  }

  function pendingWithdrawFormatter(value, row, index) {
    if( row.status == "Complete" ){
        return '····'
    } else if( row.status == "Pending" ){
        return [
            '<button onclick="setup_reconciliation();" id="reconcile-' + row.txHash + '" name="' + row.fromAddress + '-' + row.amount + '" class="btn btn-info reconcile-button" data-bs-toggle="tooltip" data-bs-placement="right">Go</button>',
            '<button onclick="cancel_reconciliation();" id="can-reconcile' + row.txHash + '" class="btn btn-warning reconcile-button" data-bs-toggle="tooltip" data-bs-placement="right">Cancel</button>'
        ].join('')
    }
  }

  function totalTextFormatter(data) {
    return 'Total'
  }

  function totalNameFormatter(data) {
    return data.length
  }

  function totalPriceFormatter(data) {
    var field = this.field
    return '$' + data.map(function (row) {
      return +row[field]
    }).reduce(function (sum, i) {
      return sum + i
    }, 0)
  }

  function initTable() {
    const txn_data = $('#meta-txn_data').data()['name'].replaceAll(`'`, `"`)
    const user_data = $('#meta-user_data').data()['name'].replaceAll(`'`, `"`)

    $('#txn_table').bootstrapTable('destroy').bootstrapTable({
      data: JSON.parse(txn_data),
      height: 600,
      columns: [
        [{
          title: 'Status',
          field: 'status',
          align: 'center',
          valign: 'middle',
          sortable: true
        }, {
          title: 'Created',
          field: 'created',
          align: 'center',
          valign: 'middle',
          sortable: true,
          footerFormatter: totalTextFormatter
        }, {
          field: 'email',
          title: 'Email',
          sortable: true,
          footerFormatter: totalNameFormatter,
          align: 'center'
        }, {
          field: 'amount',
          title: 'Amount',
          sortable: true,
          align: 'center',
          footerFormatter: totalPriceFormatter
        }, {
          field: 'txHash',
          title: 'txHash',
          sortable: true,
          align: 'center',
          formatter: etherscanlinkFormatter
        }, {
          field: 'status',
          sortable: true,
          title: 'Payout',
          align: 'center',
          formatter: pendingWithdrawFormatter
        }]
      ]
    }).bootstrapTable('sortBy', {
        field: 'status',
        sortOrder: 'desc'
    })

    $('#twitter_table').bootstrapTable('destroy').bootstrapTable({
      data: JSON.parse(user_data),
      height: 600,
      columns: [
        [{
          title: 'Username',
          field: 'username',
          align: 'center',
          valign: 'middle',
          sortable: true
        }, {
          title: 'user_id',
          field: 'user_id',
          align: 'center',
          valign: 'middle',
          sortable: true,
          footerFormatter: totalTextFormatter
        }, {
          field: 'email',
          title: 'Email',
          sortable: true,
          footerFormatter: totalNameFormatter,
          align: 'center'
        }, {
          title: 'Created',
          field: 'created',
          align: 'center',
          valign: 'middle',
          sortable: true
        }, {
          title: 'Tweet URL',
          field: 'snb_twitter_url',
          sortable: true,
          align: 'center',
          formatter: URLformatter
        }, {
          title: 'Confirm',
          align: 'center',
          formatter: 'markTweetConfirmed'
        }]
      ]
    }).bootstrapTable('sortBy', {
        field: 'created',
        sortOrder: 'desc'
    })

  }

  $(function() {
    initTable()

//    $('#locale').change(initTable)
  })