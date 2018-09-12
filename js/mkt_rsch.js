function Chart_data(category, run_date)
{
  this.name =  category;
  this.date = run_date;
  this.labels =  [];
  this.values = [];
}

$(document).ready(function(){
  $.getJSON("results.json",
function(data){
  let date_run = String(data['last_run_time']);
  delete data['last_run_time'];
  for(category in data){
    console.log(category + " -> " + data[category]);
    cht = new Chart_data(category, date_run);
    for(d in data[category]){
      console.log(d + " " + data[category][d] );
      cht.labels.push(d);
      cht.values.push(data[category][d]);
    }
    console.log("labels: " + cht.labels);
    console.log("values: " + cht.values);
    add_chart(cht.name, cht.labels, cht.values, cht.date);
  }
}
      );//close getJSON

  // Create bar chart
  function add_chart(dataset_id, data_labels, data_values, run_date){
    title = "<h1>" + dataset_id + " updated on:  " + run_date +  "</h1>";
    canvas = "<canvas id=\"" + dataset_id + "_canvas\"></canvas>";
    $("body").append("<div id=\"" + dataset_id + "_div\">" + title + canvas + "</div>");
  new Chart(document.getElementById(dataset_id + "_canvas"), {
    type: 'horizontalBar',
    data: {
      labels: data_labels,
      datasets: [
      {
        label: "Jobs for term",
        backgroundColor: "yellow",
        data: data_values 
      }
      ]
    },
    options: {
      legend: { display: false },
      title: {
        display: true,
        text: 'Jobs found requiring term'
      }
    }
  });
  }//close add_chart function
});//close jquery
