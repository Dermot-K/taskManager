$(document).ready(function () {
    // sidenav
    $(".sidenav").sidenav({ edge: "right" });

    // accordion
    $('.collapsible').collapsible();

    // tooltip
    $('.tooltipped').tooltip();

    // date picker
    $('.datepicker').datepicker({
        format: "dd mmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
});

