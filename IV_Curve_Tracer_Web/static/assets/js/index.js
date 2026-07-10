

function httpGet(theUrl)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.open("GET", theUrl, false); // false for synchronous request
    xmlHttp.send(null);
    return xmlHttp.responseText;
}


function download_CSV_btn() {
  var url = "/downloadCSV";
  
  // Create a temporary link element
  var link = document.createElement('a');
  link.href = url;
  link.download = ''; // The download attribute prompts the browser to download the file
  link.style.display = 'none'; // Hide the link
  
  // Append the link to the body
  document.body.appendChild(link);
  
  // Programmatically click the link
  link.click();
  
  // Remove the link from the document
  document.body.removeChild(link);
}


//-------------------- DATA ----------------------- //

var IVData ={};
var voltageData ={};
var currentData ={};

async function plotGraph(filename) {
  const dataIDElements = document.getElementsByClassName('data-ID');
  for (let i = 0; i < dataIDElements.length; i++) {
    dataIDElements[i].textContent = "/" + filename;
  }

  try {
    const url = '/getDataPacket/'+ (filename).replace(" ", "%20");
    const IVDataResponse = await fetch(url);
    IVData = await IVDataResponse.json();
    // console.log('Load Demand Data:', IVData);

    // Convert JSON object to array format required by ApexCharts
    const formattedIVData = Object.entries(IVData).map(([key, [voltage, current]]) => {
      return { x: parseFloat(voltage), y: current };
    });

    // Debug - Check the value 
    console.log(filename);
    console.log(formattedIVData); 
      
    // Plot graph
    new ApexCharts(document.querySelector("#reportsChart"), {
      chart: {
        type: 'line',
        height: 350,
        zoom: {
            enabled: true
        }
      },
      series: [{
          name: 'Current vs Voltage',
          data: formattedIVData
      }],
      xaxis: {
          title: {
              text: 'Voltage (V)'
          }
      },
      yaxis: {
          title: {
              text: 'Current (A)'
          }
      },
      title: {
          text: 'IV Curve of Solar Cell',
          align: 'left'
      }

    }).render();
      
  } catch (error) {
      console.error('Error fetching data:', error);
  }

  
}


// Funtion to append data from the JSON object into list
function pushValueToList(jsonObject) {
  var myList = [];
  for (var key in jsonObject) {
        myList.push(jsonObject[key]);
  } 
  console.log(myList);
  return myList;
}

function pushKeyToList(jsonObject) {
  var myList = [];
  for (var key in jsonObject) {
        myList.push(key);
  }
  console.log(myList);
  return myList;
}


//-------------------- Fetch Files ----------------------- //

// Fetch files when the page loads
document.addEventListener("DOMContentLoaded", () => {

  // Function to fetch file names to frontend
  async function fetchFiles() {
    const response = await fetch('/list_files');
    const filenames = await response.json();
    console.log(filenames)

    const sidebarNav = document.getElementById('sidebar-nav');

    filenames.forEach(filename => {
        const navItem = document.createElement('li');
        navItem.classList.add('nav-item');

        const navLink = document.createElement('a');
        navLink.classList.add('nav-link');
        navLink.addEventListener('click', function(event) {
          event.preventDefault();
          plotGraph(filename);
        });

        const span = document.createElement('span');
        span.textContent = filename;
        
        navLink.appendChild(span);
        navItem.appendChild(navLink);
        sidebarNav.appendChild(navItem);

    });
  }

  fetchFiles();

});
