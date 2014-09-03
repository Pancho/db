"use strict";
var DB = (function () {
	var r = {
			settingsTabs: ['settings', 'api', 'examples'],
			initSettings: function () {
				var hash = window.location.hash;

				hash = hash && hash.replace('#', '') || 'settings';

				if (r.settingsTabs.indexOf(hash) === -1) {
					hash = 'settings';
				}

				$('.content ol').hide();
				$('#' + hash).closest('ol').show();

				$('#navigation').on('click', 'a', function (ev) {
					var href = '#' + $(this).prop('href').split('#')[1];

					ev.preventDefault();

					$('.content ol').hide();
					$(href).closest('ol').show();
					window.location.hash = href;
				});
			}
		},
		u = {
			initialize: function () {
				r.initSettings();
			}
		};

	return u;
}());


$(function () {
	DB.initialize();
});