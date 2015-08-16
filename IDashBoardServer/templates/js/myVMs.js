
$(document).ready(function(){
    $('#myVMs-data-table').DataTable({
        dom: 'R<"row"<"#vm-count.col-sm-6"<"#vm-count-label">><"col-sm-6"f>>rt<"row"<"col-sm-6"l><"col-sm-6"p>>',
        ajax: '/get_my_VMs/',
        columns:[
            {'data': 'vm_name'},
            {'data': 'WAN_IP'},
            {'data': 'IP'},
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
            var ssh_ip_port = data.WAN_IP + ' : ' + data.port;
            hostname = data.parameter.hostname;
            username = data.parameter.username;
            memory = data.parameter.memory;
            os = data.parameter.os;
            var parameterhtml = '<div><strong>OS:</strong>' + os + '<br/><strong>Hostname:</strong>'
                + hostname + '<br><strong>Username:</strong>' + username + '<br><strong>Memory:</strong>' +  memory + 'M' + '</div>';
            var start_button = '<button class="btn btn-success startVM">Start VM</button>';
            var savestate_button = '<button class="btn btn-success savestateVM">Savestate</button>';
            var shutdown_button = '<button class="btn btn-success shutdownVM">Shutdown</button>';
            var delete_button = '<button class="btn btn-danger deleteVM" data-toggle="modal" data-target="#deleteModal">Delete VM</button>';
            if (data.state == 'online')
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
            var online_display = '<i class="fa fa-check-circle"></i> '
            var poweroff_display = '<i class="fa fa-times-circle"></i> '
            var savestate_display = '<i class="fa fa-hdd-o"></i> '
            var state_display = ''
            if (data.state === 'online')
                state_display = online_display + data.state
            else if (data.state === 'poweroff')
                state_display = poweroff_display + data.state
            else
                state_display = savestate_display + data.state
            $('td:eq(1)', row).html(ssh_ip_port);
            var statehtml = '<div class="vm_state"><a href=/detail/' + data.id + '/ >' + state_display + '</a></div>';
            $('td:eq(5)', row).html(treatmenthtml);
            $('td:eq(4)', row).html(parameterhtml);
            $('td:eq(3)', row).html(statehtml);
        },
        drawCallback: function () {
            var myVMCount = this.api().data().length;
            var online_display = '<i class="fa fa-check-circle"></i> online'
            var poweroff_display = '<i class="fa fa-times-circle"></i> poweroff'
            var savestate_display = '<i class="fa fa-hdd-o"></i> savestate'
            $('#vm-count-label').html('<label>I have <strong> ' + myVMCount + ' </strong> Virtual Machines.</label>');
            if (myVMCount != 0) {
                // 单击单元格跳转到详细信息
                $('#myVMs-data-table tr').on('click', 'button.startVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button').addClass('disabled');
                    $(this).parents('tr').find('.vm_state').html('<img src="/img/loading.gif" alt=""/>');
                        $.post('/control_vm/', {'id': id, 'request_type': 'start'}, function(response){
                                var response_json = eval('(' + response + ')');
                                if (response_json.request_result === 'success'){
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + online_display +'</a></div>');
                                    $("[data-id="+id+"]").find('.shutdownVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.savestateVM').removeClass('disabled');
                                }
                                else {
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + poweroff_display + '</a></div>');
                                    $("[data-id="+id+"]").find('.startVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.deleteVM').removeClass('disabled');
                                    alert('error: ' + response_json.error_information)
                                }
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.shutdownVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button').addClass('disabled');
                    $(this).parents('tr').find('.vm_state').html('<img src="/img/loading.gif" alt=""/>');
                        $.post('/control_vm/', {'id': id, 'request_type': 'shutdown'}, function(response){
                                var response_json = eval('(' + response + ')');
                                if (response_json.request_result === 'success'){
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + poweroff_display + '</a></div>');
                                    $("[data-id="+id+"]").find('.startVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.deleteVM').removeClass('disabled');
                                }
                                else {
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + online_display +'</a></div>');
                                    $("[data-id="+id+"]").find('.shutdownVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.savestateVM').removeClass('disabled');
                                    alert('error: ' + response_json.error_information)
                                }
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.savestateVM', function () {
                    var id = $(this).parentsUntil('tbody').last().attr('data-id');
                    $(this).addClass('disabled');
                    $(this).siblings('button').addClass('disabled');
                    $(this).parents('tr').find('.vm_state').html('<img src="/img/loading.gif" alt=""/>');
                        $.post('/control_vm/', {'id': id, 'request_type': 'savestate'}, function(response){
                                var response_json = eval('(' + response + ')');
                                if (response_json.request_result === 'success'){
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + savestate_display +'</a></div>');
                                    $("[data-id="+id+"]").find('.startVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.deleteVM').removeClass('disabled');
                                }
                                else {
                                    $("[data-id="+id+"]").find('.vm_state').html('<a href=/detail/' + id + '/ >' + online_display +'</a></div>');
                                    $("[data-id="+id+"]").find('.savestateVM').removeClass('disabled');
                                    $("[data-id="+id+"]").find('.shutdownVM').removeClass('disabled');
                                    alert('error: ' + response_json.error_information)
                                }
                        }
                    );
                });
                $('#myVMs-data-table tr').on('click', 'button.deleteVM', function () {
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