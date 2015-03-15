var refreshInterval = 0;
var clockId = -1;

$(document).ready(function() {

	// 数据表插件初始化
	$('#main-data-table').DataTable({
		dom: 'R<"row"<"#vm-count.col-sm-6"><"col-sm-6"f>>rt<"row"<"col-sm-6"l><"col-sm-6"p>>',
		ajax: '/refreshSimplePage/',
		columns: [
			{'data': 'ip'},
			{'data': 'os'},
			{'data': 'HostName'},
			{'data': 'UserName'},
			{'data': 'Memory'},
			{'data': 'remark'}
		],
		responsive: {
			details: {
				renderer: function(api, rowIndex) {
					// 响应式插件中child单元格的渲染函数
					var html = api.cells(rowIndex, ':hidden').eq(0).map(function(cell) {
						var header = $(api.column(cell.column).header());

						var title = '<span class="dtr-title">' + header.text() + ':' + '</span>';
						var data = '<span class="dtr-data">' + api.cell(cell).data() + '</span>';

						return '<li data-dtr-index="' + cell.column + '">' + title + data + '</li>';
					}).toArray().join('');

					var row = api.row(rowIndex).node();
					var id = $(row).attr('data-id');

					return $('<ul data-dtr-index="0" data-id="' + id + '"></ul>').append(html);
				}
			}
		},
		initComplete: function() {
			console.log('init complete');
			var vmCount = this.api().data().length;
			// 显示在线虚拟机数量
			$('#vm-count').html('<label><strong> ' + vmCount + ' </strong> virtual machines online.</label>');
			// 添加刷新按钮组
			$('#vm-count').prepend($('#refresh-button-group'));
			if (vmCount != 0) {
				// 单击单元格跳转到详细信息
				$('#main-data-table tbody').on('click', 'tr', function() {
					console.log($(this).attr('data-id'));
					$(location).attr('href', '/detail/' + $(this).attr('data-id') + '/');
				});
				// 单击响应式插件生成的child单元格跳转到详细信息
				$('#main-data-table tbody').on('click', 'ul', function(e) {
					console.log($(this).attr('data-id'));
					$(location).attr('href', '/detail/' + $(this).attr('data-id') + '/');
					e.stopPropagation();
				});
			}
		},
		createdRow: function(row, data) {
			// 为每一行赋予一个虚拟机id
			$(row).attr('data-id', data.id);
		},
		rowCallback: function(row, data) {
			// 修改占用率为进度条样式
			var percent = data.Memory;
			var html = '<div class="progress" style="margin-bottom: 0px;"><div class="progress-bar" role="progressbar" style="min-width: 2em; width: ' + percent + '%;">' + percent + '%</div></div>';
			$('td:eq(4)', row).html(html);

			// 去掉Operating System中末尾的符号
			// 这部分最好后台来做
			var osText = $('td:eq(1)', row).text();
			$('td:eq(1)', row).text(osText.substring(0, osText.length - 8));
		}
	});

	// 为datatable插件应用bootstrap样式
	$('#main-data-table').removeClass('display').addClass('table table-striped table-bordered table-hover');
	
	// // DataTable插件的FixedHeader扩展，响应式表现较差，暂不使用
	// new $.fn.dataTable.FixedHeader($('#main-data-table').DataTable());

	// 刷新表格数据按钮
	$('#refresh-button').click(refreshData);
});

/**
 * 设置自动刷新时间
 */
function setRefreshOption(interval, index) {
	clearInterval(clockId);
	if (interval > 0) {
		clockId = setInterval(refreshData, interval * 1000);
	}
	console.log('interval set to ' + interval);
	// 更新UI
	$('#refresh-option-menu span.glyphicon-check').removeClass('glyphicon-check').addClass('glyphicon-unchecked');
	$('#refresh-option-menu span').eq(index).removeClass('glyphicon-unchecked').addClass('glyphicon-check');
}

/**
 * 刷新DataTable数据
 */
function refreshData() {
	console.log('reload start');
	$('#main-data-table').DataTable().ajax.reload(function() {
		console.log('reload complete');
	}, false);
}