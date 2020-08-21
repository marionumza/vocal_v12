$(document).ready(function () {
    odoo.define('mkt_membership_ext.pricing_switcher', function (require){
        $(document).on('change', '.pricing-switcher input[id="monthly-1"]', function () {
            $('#monthly').show();
            $('#yearly').hide();
        });
        $(document).on('change', '.pricing-switcher input[id="yearly-1"]', function () {
            $('#monthly').hide();
            $('#yearly').show();
        });
    });
});


