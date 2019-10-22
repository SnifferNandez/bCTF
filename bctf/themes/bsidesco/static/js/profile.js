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
            text: 'Retos',
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

function solvedLineChart(ctx, dataset, team_color) {

    datasets = []
    datasets.push($.parseJSON(JSON.stringify(dataset)));

    var chartData = {
        datasets: datasets,
    }
    var solvedLineChart = new Chart(ctx,{
        type: 'scatter',
        data: chartData,
        options: {
 
            legend: {
                position: 'bottom',
                labels: {
                    fontColor: "#fff",
                    usePointStyle: true,
                }
            },
            title: {
                display: true,
                text: 'Progreso',
                fontSize: 18,
                fontColor: '#fff'
            },
            scales: {
                xAxes: [{
                    type: 'time',
                    ticks: {
                        fontColor: "#fff",
                        beginAtZero: false
                    },
                    gridLines: {
                        display:false
                    } 
                }],
                yAxes: [{
                    ticks: {
                        fontColor: "#fff",
                    },
                    gridLines: {
                        display:false
                    }   
                }]
            }
        }
    });

}  


function cumulativesum (arr) {
    var result = arr.concat();
    for (var i = 0; i < arr.length; i += 1){
        result[i] = arr.slice(0, i + 1).reduce(function(p, i){ return p + i; });
    }
    return result
}

function colorhash(str) {
    var hash = 0;
    for (var i = 0; i < str.length; i += 1) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    var colour = '#';
    for (var i = 0; i < 3; i += 1) {
      var value = (hash >> (i * 8)) & 0xFF;
      colour += ('00' + value.toString(16)).substr(-2);
    }
    return colour;
  }

  String.prototype.hashCode = function() {
    var hash = 0, i, chr, len;
    if (this.length == 0) {
        return hash;
    }
    for (i = 0, len = this.length; i < len; i += 1) {
        chr   = this.charCodeAt(i);
        hash  = ((hash << 5) - hash) + chr;
        hash |= 0; // Convert to 32bit integer
    }
    return hash;
};