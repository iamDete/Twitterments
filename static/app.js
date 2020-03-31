$(document).ready(function() {

    $('#table_view').DataTable();
    $('[data-toggle="tooltip"]').tooltip()


    var positive = $(".1").length
    var neutral = $(".0").length
    var negative = $(".-1").length

    $("#noPos").text(positive)
    $("#noNeg").text(negative)
    $("#noNeu").text(neutral)

    var total = positive + neutral + negative
    $("#totalRes").text(neutral + positive + negative)
    $("#realRes").text(neutral + positive + negative)
    $("#num").val(neutral + positive + negative)

    $(".dropdown-item").click(function() {
        var val = $(this).attr( "value" )

        if(val == -1) {
            $(".1").addClass("d-none")
            $(".0").addClass("d-none")

            $("#totalRes").text(negative)

            $(".-1").removeClass("d-none")
        } else if (val == 1) {

            $(".-1").addClass("d-none")
            $(".0").addClass("d-none")

            $("#totalRes").text(positive)

            $(".1").removeClass("d-none")
        } else if (val == 0) {

            $(".-1").addClass("d-none")
            $(".1").addClass("d-none")

             $("#totalRes").text(neutral)

            $(".0").removeClass("d-none")
        } else {
            $(".0").removeClass("d-none")
            $(".1").removeClass("d-none")
            $(".-1").removeClass("d-none")

            $("#totalRes").text(neutral + positive + negative)
        }

    })

//    var prevScrollpos = window.pageYOffset;
//    window.onscroll = function() {
//      var currentScrollPos = window.pageYOffset;
//      if (prevScrollpos > currentScrollPos) {
//        document.getElementById("navbar").style.top = "0";
//      } else {
//        document.getElementById("navbar").style.top = "-50px";
//      }
//      prevScrollpos = currentScrollPos;
//    }


})
