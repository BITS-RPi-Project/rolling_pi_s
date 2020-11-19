$(document).ready(() => {

    $.ajax({
        url: "http://localhost:3000/data",
        //method: 'GET',
        dataType: 'json',
        success: function(response) {

            var arrLabels = new Array(response.rows.length);

            for (let i = 0; i < response.rows.length; i++) {

                arrLabels[i] = response.rows[i].dateTime

            }

            var arrData = new Array(response.rows.length);

            for (let i = 0; i < response.rows.length; i++) {

                arrData[i] = response.rows[i].level

            }

            var ctx = document.getElementById('myChart').getContext('2d');

            var chart = new Chart(ctx, {
                // The type of chart we want to create
                type: 'line',

                // The data for our dataset
                data: {
                    labels: arrLabels,
                    datasets: [{
                        label: 'Tank Level',
                        borderColor: 'orange',
                        data: arrData
                    }]
                },

                // Configuration options go here
                options: {
                    // responsive: true,
                    // maintainAspectRatio: true


                }
            });



        }

    })
})