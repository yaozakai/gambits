//$(function() {
//    var txn_data = $('#meta-txn_data').data()['name']
//    txn_data = txn_data.replaceAll(`'`, `"`)
//    $('#txn_table').bootstrapTable({data: JSON.parse(txn_data), height: 700 })
////        $table.bootstrapTable({data: data })
//})

//var $table = $('#txn_table')
  var $remove = $('#remove')
  var selections = []

  function getIdSelections() {
    return $.map($table.bootstrapTable('getSelections'), function (row) {
      return row.id
    })
  }

  function responseHandler(res) {
    $.each(res.rows, function (i, row) {
      row.state = $.inArray(row.id, selections) !== -1
    })
    return res
  }

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
    return '<a href="https://etherscan.io/address/' + data + ' target="_blank">' + data.slice(0, 6) + '..' + data.slice(-3) + '</a>'
  }

  function pendingWithdrawFormatter(value, row, index) {
    if( row.status == "Complete" ){
        return '····'
    } else if( row.status == "Pending" ){
        return '<button onclick="setup_reconciliation();" id="reconcile-' + row.txHash + '" name="' + row.fromAddress + '-' + row.amount + '" class="btn btn-link reconcile-button" id="reconcile-go" data-bs-toggle="tooltip" data-bs-placement="right">Go</button>' +
        '<button onclick="cancel_reconciliation();" id="' + row.amount + '-' + row.txHash + '" class="btn btn-link reconcile-button" id="reconcile-go" data-bs-toggle="tooltip" data-bs-placement="right">Cancel</button>'
    }



    console.log(row)
//    return '<button onclick="cancel_reconciliation();" id="{{ record.amount }}-{{ record.txHash }}" class="btn btn-link reconcile-button" id="reconcile-go" data-bs-toggle="tooltip" data-bs-placement="right">Cancel</button>'
    return [
      '<a class="like" href="javascript:void(0)" title="Like">',
      '<i class="fa fa-heart"></i>',
      '</a>  ',
      '<a class="remove" href="javascript:void(0)" title="Remove">',
      '<i class="fa fa-trash"></i>',
      '</a>'
    ].join('')
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
      return +row[field].substring(1)
    }).reduce(function (sum, i) {
      return sum + i
    }, 0)
  }

  function statusSorter(a, b) {
    return a - b
  }

  function filter_complete() {

//      if( pendingWithdrawFilter == 0) {
//          $('#txn_table').bootstrapTable('remove', {
//            field: 'status',
//            values: 'Complete'
//          })
//          pendingWithdrawFilter = 1
//      } else {
//          $('#txn_table').bootstrapTable('append', {
//            field: 'status',
//            values: 'Complete'
//          })
//          pendingWithdrawFilter = 0
//      }
  }

  function initTable() {
    const txn_data = $('#meta-txn_data').data()['name'].replaceAll(`'`, `"`)
//    const txn_data_rows = txn_data['rows'].replaceAll(`'`, `"`)
//    $('#txn_table').bootstrapTable({data: JSON.parse(txn_data), height: 700 })

    $('#txn_table').bootstrapTable('destroy').bootstrapTable({
      data: JSON.parse(txn_data),
      height: 750,
//      locale: $('#locale').val(),
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
//    $('#txn_table').on('check.bs.table uncheck.bs.table ' +
//      'check-all.bs.table uncheck-all.bs.table',
//    function () {
//      $remove.prop('disabled', !$('#txn_table').bootstrapTable('getSelections').length)
//
//      // save your data, here just save the current page
//      selections = getIdSelections()
//      // push or splice the selections if you want to save all data selections
//    })
//    $('#txn_table').on('all.bs.table', function (e, name, args) {
//      console.log(name, args)
//    })
//    $remove.click(function () {
//      var ids = getIdSelections()
//      $('#txn_table').bootstrapTable('remove', {
//        field: 'id',
//        values: ids
//      })
//      $remove.prop('disabled', true)
//    })
  }

  $(function() {
    initTable()

//    $('#locale').change(initTable)
  })