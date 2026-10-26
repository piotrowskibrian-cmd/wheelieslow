// Shows "in N days" / "finished" next to each race, based on today's date.
(function () {
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  var races = document.querySelectorAll('.race[data-date]');
  races.forEach(function (el) {
    var parts = el.getAttribute('data-date').split('-');
    var d = new Date(+parts[0], +parts[1] - 1, +parts[2]);
    var days = Math.round((d - today) / 86400000);
    var out = el.querySelector('.race-countdown');
    if (!out) return;
    if (days > 1) out.textContent = 'in ' + days + ' days';
    else if (days === 1) out.textContent = 'tomorrow';
    else if (days === 0) out.textContent = 'race day';
    else out.textContent = '';
  });
})();
