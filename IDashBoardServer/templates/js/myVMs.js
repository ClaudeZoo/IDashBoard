/**
 * Created by wcx on 15/4/28.
 */
$(document).ready(function(){
    $('#myVMs-data-table').DataTable({
        dom: 'R<"row"<"#vm-count.col-sm-6"<"#vm-count-label">><"col-sm-6"f>>rt<"row"<"col-sm-6"l><"col-sm-6"p>>',
        ajax: '/get_my_VMs/',
        columns:[
            {'data': 'uuid'},
            {'data': 'port'},
            {'data': 'state'},
			{'data': 'parameter'},
            {'data': 'treatment'}
        ],
        initComplete: function(){
            //$('#host-count').prepend($('#refresh-button-group'));
        },
        createdRow: function(row, data) {
			// 为每一行赋予一个虚拟机id
			$(row).attr('data-id', data.id);
		},
        rowCallback: function(row, data) {
            hostname = data.parameter.hostname;
            username = data.parameter.username;
            memory = data.parameter.memory;
            os = data.parameter.os;
            osset = ['ubuntu 14.04 LTS'];
            memoryset = ['512M', '1024M'];
            var states = ["online", "offline", "savestate"];
            var parameterhtml = '<div><strong>OS:</strong>' + osset[os - 1] + '<br/><strong>Hostname:</strong>'
                + hostname + '<br><strong>Username:</strong>' + username + '<br><strong>Memory:</strong>' +  memoryset[memory - 1] + '</div>';
            var start_button = '<button class="btn btn-success startVM">Start VM</button>';
            var savestate_button = '<button class="btn btn-success savestateVM">Savestate</button>';
            var shutdown_button = '<button class="btn btn-success shutdownVM">Shutdown</button>';
            var delete_button = '<button class="btn btn-danger deleteVM" data-toggle="modal" data-target="#deleteModal">Delete VM</button>';
            if (data.state == 0)
            {
                start_button = '<button class="btn btn-success startVM disabled">Start VM</button>';
                delete_button = '<button class="btn btn-danger deleteVM disabled" data-toggle="modal" data-target="#deleteModal">Delete VM</button>';
            }
            else
            {
                savestate_button = '<button class="btn btn-success savestateVM disabled">Savestate</button>';
                shutdown_button = '<button class="btn btn-warning shutdownVM disabled">Shutdown</button>';
            }
            var treatmenthtml = '<div>'+ start_button + savestate_button + shutdown_button + delete_button + '</div>';
            var statehtml = '<a href=/detail/' + data.id + '/ >'+states[data.state]+'</a>';
            $('td:eq(4)', row).html(treatmenthtml);
            $('td:eq(3)', row).html(parameterhtml);
            $('td:eq(2)', row).html(statehtml);
        },
        drawCallback: function () {
            var myVMCount = this.api().data().length;
            $('#vm-count-label').html('<label>I have <strong> ' + myVMCount + ' </strong> Virtual Machines.</label>');
            if (myVMCount != 0) {
                // 单击单元格跳转到详细信息
                $('#myVMs-data-table tr').on('click', 'button.startVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button.savestateVM').removeClass('disabled');
                    $(this).siblings('button.shutdownVM').removeClass('disabled');
                    $(this).siblings('button.deleteVM').addClass('disabled');
                    $(this).parent().parent().parent().children().eq(2).html("loading");
                    json_obj = {'id': id}
                        $.post('/start_apply/', JSON.stringify(json_obj), function(data){
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.shutdownVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button.deleteVM').removeClass('disabled');
                    $(this).siblings('button.startVM').removeClass('disabled');
                    $(this).siblings('button.savestateVM').addClass('disabled');
                    $(this).parent().parent().parent().children().eq(2).html("loading");
                    json_obj = {'id': id}
                        $.post('/stop_apply/', JSON.stringify(json_obj), function(data){
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.savestateVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button.deleteVM').removeClass('disabled');
                    $(this).siblings('button.startVM').removeClass('disabled');
                    $(this).siblings('button.shutdownVM').addClass('disabled');
                    $(this).parent().parent().parent().children().eq(2).html("loading");
                    json_obj = {'id': id}
                        $.post('/savestate_apply/', JSON.stringify(json_obj), function(data){
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.deleteVM', function () {
                    $(this).addClass('disabled');
                    $(this).siblings('button.savestateVM').addClass('disabled');
                    $(this).siblings('button.startVM').addClass('disabled');
                    $(this).siblings('button.shutdownVM').addClass('disabled');
                    $("#deleteModal").attr("data-id", $(this).parentsUntil('tbody').last().attr('data-id'))
                });
            }
        }
    });
    $('#myVMs-data-table').removeClass('display').addClass('table table-striped table-bordered table-hover');
});

function confirmDelete(data_id){
    json_obj = {'id': $('#deleteModal').attr('data-id')}

    //$('#myVMs-data-table').find('tr[data-id='+$('#deleteModal').attr('data-id')+"]").find('td').last().html("please wait...");
    $.post('/delete_apply/', JSON.stringify(json_obj), function(data){
        }
    );
}