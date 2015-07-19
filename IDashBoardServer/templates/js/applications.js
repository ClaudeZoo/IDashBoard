/**
 * Created by wcx on 15/4/28.
 */

$(document).ready(function(){
    $('#application-data-table').DataTable({
        dom: 'R<"row"<"#vm-count.col-sm-6"<"#vm-count-label">><"col-sm-6"f>>rt<"row"<"col-sm-6"l><"col-sm-6"p>>',
        ajax: '/get_my_applications/',
        columns:[
            {'data': 'submissionTime'},
			{'data': 'parameter'},
			{'data': 'type'},
            {'data': 'state'}
        ],
        "ordering": true,
        "order": [[ 0, "desc" ]],
        initComplete: function(){
            //$('#vm-count').prepend($('#refresh-button-group'));
        },
        createdRow: function(row, data) {
			// 为每一行赋予一个虚拟机id
			$(row).attr('data-id', data.id);
		},
        rowCallback: function(row, data) {
            memory = data.parameter.memory;
            os = data.parameter.os;
            vm_type = data.parameter.vm_type;
            if(data.type=='new'){
                var parameterhtml = '<div><strong>vm_type:</strong>' + vm_type + '<br><strong>os:</strong>' + os + '<br><strong>memory:</strong>' +  memory + 'M</div>';
            }
            else{
                parameterhtml = '<div><strong>uuid:</strong>'+ data.parameter.uuid+'</div>'
            }
            $('td:eq(3)', row).html(data.state);
            $('td:eq(1)', row).html(parameterhtml);
        },
        drawCallback: function () {
            var applicationCount = this.api().data().length;
            $('#vm-count-label').html('<label>I have <strong> ' + applicationCount + ' </strong> historical applications.</label>');
        }
    });
    $('#application-data-table').removeClass('display').addClass('table table-striped table-bordered table-hover');
});