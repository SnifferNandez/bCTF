function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

function randomColors(data_length) {
    var colors = [];
    for (var i = 0; i < data_length; i++ ) {
        colors.push(getRandomColor());
    }
    return colors;
}

 function solvedChart(ctx, data) {

    data = {
        datasets: [{
            data: data,
            backgroundColor: ['green', 'red']
        }],

        labels: [
            'Resueltos',
            'Pendientes'
        ]
    };

    options = {
        maintainAspectRatio : false,
        title: {
            display: true,
            text: 'Reto resuelto',
            fontSize: 30,
            fontColor: 'white'
        },
        legend: {
            labels: {
                fontColor: "white",
                fontSize: 15
            }
        }
    }

    var solvedChart = new Chart(ctx,{
        type: 'doughnut',
        data: data,
        options: options
    });

 }  


  function solvedAtLeastOne(ctx, data) {

    data = {
        datasets: [{
            data: data,
            backgroundColor: ['green', 'red']
        }],

        labels: [
            'Uno o mas',
            'Nope'
        ]
    };

    options = {
        maintainAspectRatio : false,
        title: {
            display: true,
            text: 'Equipos que puntuaron!',
            fontSize: 30,
            fontColor: 'white'
        },
        legend: {
            labels: {
                fontColor: "white",
                fontSize: 15
            }
        }
    }

    var solvedChart = new Chart(ctx,{
        type: 'doughnut',
        data: data,
        options: options
    });

 }  

  function firstBloods(ctx, labels, data) {
    data = {
        datasets: [{
            data: data,
            backgroundColor: randomColors(data.length)
        }],
        borderWidth: 1,
        labels: labels,
    };

    options = {
        maintainAspectRatio : false,

        title: {
            display: true,
            text: 'Primeras capturas!',
            fontSize: 30,
            fontColor: 'white'
        },
        legend: {
            labels: {
                fontColor: "white",
                fontSize: 15
            }
        }
    }

    var solvedChart = new Chart(ctx,{
        type: 'pie',
        data: data,
        options: options
    });

 }  
