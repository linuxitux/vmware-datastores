/*
 * TODO: Agregar espacio libre al detalle
 *
 */

var m = [];
var scale = 'absolute';

function updateMetrics() {

    // Get fresh stats
    var getJSON = function(url, successHandler, errorHandler) {
        var xhr = typeof XMLHttpRequest != 'undefined'
            ? new XMLHttpRequest()
            : new ActiveXObject('Microsoft.XMLHTTP');
        xhr.open('get', url, true);
        xhr.onreadystatechange = function() {
            var status;
            var data;
            // https://xhr.spec.whatwg.org/#dom-xmlhttprequest-readystate
            if (xhr.readyState == 4) {
                status = xhr.status;
                if (status == 200) {
                    data = JSON.parse(xhr.responseText);
                    successHandler && successHandler(data);
                }
                else {
                    errorHandler && errorHandler(status);
                }
            }
        };
        xhr.send();
    };

    // Parse JSON response
    getJSON('list_datastore_space', function(data) {

        // Obtener el div principal "container"
        var container = document.getElementById('container');

        // Fecha del reporte
        var fecha = '';

        // Por cada elemento en la estructura JSON
        for (var i=0; i<Object.keys(data).length; i++) {
            // Recuperar datastore
            var datastore_name = Object.keys(data)[i];

            // Si el nombre empieza con "ds-local", ignorarlo
            if (datastore_name.startsWith('ds-local')) {
                continue;
            }

            var datastore = data[datastore_name];

            // Si se trata de la fecha, guardarla en la variable fecha
            if (datastore_name.startsWith('fecha')) {
                fecha = datastore;
                continue;
            }

            // Crear div
            var graph = document.createElement('div');
            graph.className = 'metrics-container';
            graph.innerHTML = '<h4>'+datastore_name+'</h4>';

            var menu = document.createElement('div');
            menu.className = 'metrics-menu';

            // Insertar link al detalle
            var dlink = document.createElement('a');
            dlink.setAttribute('href', 'datastore_detail?ds='+datastore_name);
            dlink.setAttribute('class', 'button');
            dlink.innerHTML = '+DETALLE';
            menu.appendChild(dlink);

            // Separador
            var separator = document.createElement('span');
            separator.setAttribute('class', 'separator');
            separator.innerHTML = ' | ';
            menu.appendChild(separator);

            // Insertar link al reporte
            var rlink = document.createElement('a');
            rlink.setAttribute('href', 'datastore_report?ds='+datastore_name);
            rlink.setAttribute('class', 'button');
            rlink.innerHTML = 'REPORTE';
            menu.appendChild(rlink);

            graph.appendChild(menu);

            // Crear canvas
            var canvas = document.createElement('canvas');
            canvas.setAttribute('id', datastore_name);
            canvas.setAttribute('width', '200px');
            canvas.setAttribute('height', '200px');
            graph.appendChild(canvas);

            // Insertar gráfico
            container.appendChild(graph);

            // Dibujar gráfico de torta
            drawPie(canvas.getContext('2d'),
                canvas.width,
                canvas.height,
                datastore.pfree,0.9);

            // Dibujar tabla
            drawTable(graph,datastore);

        }

        // Insertar fecha
        var pdate = document.getElementById('fecha');
        // Eliminar segundos de la hora
        fecha = fecha.substr(0,fecha.lastIndexOf(':'));
        // Formatear fecha
        var afecha = fecha.split(' ');
        var adia = afecha[0].split('-');
        var dia = adia[2]+'/'+adia[1]+'/'+adia[0];
        var nfecha = dia+' '+afecha[1];
        pdate.innerHTML = '<b>Última actualización:</b> '+nfecha;
        pdate.style['display'] = 'block';

    }, function(status) {
        //alert('Something went wrong.');
    });

}

function drawPie(canvas,w,h,value,factor) {

    // Center coordinates
    var cx = w/2;
    var cy = h/2;

    // Radius
    var radius = cx * factor;

    // Clear canvas
    canvas.clearRect(0,0,canvas.width,canvas.height);

    // Starting and ending angles
    var startAngle_used = 0;
    var endAngle_used = 2*Math.PI*value/100;
    var startAngle_free = endAngle_used;
    var endAngle_free = 2*Math.PI;

    // Draw used space
    canvas.beginPath();
    canvas.moveTo(cx,cy);
    canvas.arc(cx, cy, radius, startAngle_used, endAngle_used, true);
    canvas.closePath();
    canvas.fillStyle = "#F2784B";
    canvas.fill();

    // Draw free space
    canvas.beginPath();
    canvas.moveTo(cx,cy);
    canvas.arc(cx, cy, radius, startAngle_free, endAngle_free, true);
    canvas.fillStyle = "#66CC99";
    canvas.fill();
}

function drawTable(cont,datastore) {
    var capacity = datastore.capacity;
    var free = datastore.free;
    var used = datastore.used;
    var pfree = datastore.pfree;

    var div = document.createElement('div');
    div.className = 'metrics-table';
    var table = '<table>';
    table += '<tr><td><li class="utilizado">Utilizado</li></td><td class="metric-value">'+used+'</td></tr>';
    table += '<tr class="beforeseparator"><td><li class="disponible">Disponible</li></td><td class="metric-value">'+free+'</td></tr>';
    table += '<tr class="afterseparator"><td class="smallcaps">Capacidad</td><td class="metric-value">'+capacity+'</td></tr>';
    table += '<tr><td class="smallcaps">Disponible (%)</td><td class="metric-value">'+pfree+'&nbsp;&nbsp;</td></tr>';
    table += '</table>';
    div.innerHTML = table;
    cont.appendChild(div);
}

function createGraphics() {
    updateMetrics();
}

function updateReport(ds) {

    // Get fresh stats
    var getJSONreport = function(url, successHandler, errorHandler) {
        var xhr = typeof XMLHttpRequest != 'undefined'
            ? new XMLHttpRequest()
            : new ActiveXObject('Microsoft.XMLHTTP');
        xhr.open('get', url, true);
        xhr.onreadystatechange = function() {
            var status;
            var data;
            // https://xhr.spec.whatwg.org/#dom-xmlhttprequest-readystate
            if (xhr.readyState == 4) {
                status = xhr.status;
                if (status == 200) {
                    data = JSON.parse(xhr.responseText);
                    successHandler && successHandler(data);
                }
                else {
                    errorHandler && errorHandler(status);
                }
            }
        };
        xhr.send();
    };

    // Parse JSON response
    getJSONreport('report_datastore_space?ds='+ds, function(data) {

        // Obtener el div principal "container"
        var container = document.getElementById('container');

        var fecha_inicio = data[0][0];
        var fecha_fin = data[(data.length)-1][0];

        // Arreglo de muestras
        m = [];

        // Por cada elemento en la estructura JSON
        for (var i=0; i<data.length; i++) {
            // Recuperar porcetaje UTILIZADO
            m.push(100-parseFloat(data[i][2]));
        }

        // Ahora m contiene todas las mediciones

        // Crear div para el gráfico
        var graph = document.createElement('div');
        graph.className = 'report-container';
        graph.innerHTML = '<h4>'+ds+'</h4><p>Reporte de espacio utilizado ('+fecha_inicio+' - '+fecha_fin+')</p>';

        // Crear canvas
        var canvas = document.createElement('canvas');
        canvas.setAttribute('id', ds);
        canvas.setAttribute('width', (window.innerWidth)*0.8);
        canvas.setAttribute('height', (window.innerHeight)*0.5);
        graph.appendChild(canvas);

        // Insertar gráfico
        container.appendChild(graph);

        // Dibujar reporte
        drawReport(canvas.getContext('2d'),
            canvas.width,
            canvas.height,
            m,
            scale);

        // Insertar leyenda
        var br = document.createElement('br');
        graph.appendChild(br);
        br = document.createElement('br');
        graph.appendChild(br);
        var plegend = document.createElement('p');
        plegend.setAttribute('class', 'legend');
        plegend.innerHTML = '% Utilizado';
        graph.appendChild(plegend);

        /* Insertar enlaces */
        // Enlace "Cambiar escala"
        var cslink = document.createElement('a');
        cslink.setAttribute('href', 'javascript:changeScale(\''+ds+'\')');
        cslink.setAttribute('class', 'button');
        cslink.innerHTML = 'Cambiar escala';
        graph.appendChild(cslink);
        // Separador
        var separator = document.createElement('span');
        separator.setAttribute('class', 'separator');
        separator.innerHTML = ' | ';
        graph.appendChild(separator);
        // Enlace "Volver"
        var rlink = document.createElement('a');
        rlink.setAttribute('href', 'dashboard');
        rlink.setAttribute('class', 'button');
        rlink.innerHTML = 'Volver';
        graph.appendChild(rlink);

    }, function(status) {
        //alert('Something went wrong.');
    });

}

function drawReport(canvas,w,h,data,scale) {

    // Clear canvas
    canvas.clearRect(0,0,w,h);

    // Colors
    var c_used = "#F2784B";
    var c_background = "#F2F1EF";

    // Defino límites en píxeles
    var minx = w*0.05;
    var maxx = w*0.95;
    var miny = h*0.05;
    var maxy = h*0.95;

    // Dimensiones para el gráfico
    var ancho = maxx - minx;
    var alto = maxy - miny;

    // Obtener valores mínimo y máximo
    var minv = "nulo";
    var maxv = 0;

    var valor = 0;

    switch (scale) {
        case 'absolute':
            minv = 0;
            maxv = 100;
            break
        case 'relative':
            // Recorrer la tabla para obtener los valores mínimo y máximo
            for (var i=0; i<data.length; i++) {
                valor = data[i];
                if (minv == "nulo" || minv > valor) {
                    minv = valor;
                }
                if (maxv < valor) {
                    maxv = valor;
                }
            }
            break;
    }

    // Escala
    /*
        Se utiliza para adaptar los valores de la tabla
        en las dimensiones del canvas
    */
    var escala = maxv - minv;

    /* Dibujar ordenadas */

    canvas.beginPath();
    canvas.font = '12px Calibri';
    canvas.lineWidth = 1;
    canvas.fillStyle = c_used;

    switch (scale) {
        case 'absolute':
            // Obtengo el siguiente valor
            valor = data[data.length-1];
            y = maxy - (valor-minv) * (alto/escala); // calculo el siguiente punto
            canvas.fillText(data[data.length-1].toFixed(2), 0, y);
            break;
        case 'relative':
            for (var i=0; i<data.length; i++) {
                // Obtengo el siguiente valor
                valor = data[i];
                // NO imprimir dos veces el mismo valor en el eje Y
                if(i > 0 && Math.floor(valor*100) == Math.floor(data[i-1]*100)) continue;
                y = maxy - (valor-minv) * (alto/escala); // calculo el siguiente punto
                canvas.fillText(data[i].toFixed(2), 0, y);
            }
            break;
    }
    canvas.stroke();

    /* Dibujar recuadro */

    canvas.beginPath();
    canvas.fillStyle = c_background;
    //canvas.setLineDash([0,0]);
    //canvas.lineWidth = 1;
    canvas.fillRect(minx,miny-20,maxx-minx,maxy-miny+40);

    /* Dibujar líneas */

    canvas.strokeStyle = c_used;
    canvas.fillStyle = c_used;

    // Calculo el primer valor
    valor = data[0];
    var x = minx;
    var y = maxy - (valor-minv) * (alto/escala);

    // Dibujo el primer valor (punto)
    canvas.fillRect(x-2,y-2,4,4);
    canvas.moveTo(x,y);

    // Desde el segundo hasta el último valor
    for (var i=1; i<data.length; i++) {
        x += ancho/(data.length-1); // avanzo las abcisas
        valor = data[i]; // obtengo el siguiente valor
        y = maxy - (valor-minv) * (alto/escala); // calculo el siguiente punto
        canvas.lineTo(x,y); // dibujo una línea entre ambos puntos
        canvas.fillRect(x-2,y-2,4,4); // dibujo el nuevo punto
    }
    canvas.stroke();
}

function createReport(ds){
    updateReport(ds);
}

function changeScale(ds) {
    // Obtener el objeto canvas
    var canvas = document.getElementById(ds);
    if (scale == 'absolute') {
        scale = 'relative';
    }
    else {
        scale = 'absolute';
    }
    if (m.length == 0) {
        // Si no hay datos, realizar la solicitud nuevamente
        updateReport(ds);
        return;
    }
    // Dibujar reporte
    drawReport(canvas.getContext('2d'),
        canvas.width,
        canvas.height,
        m,
        scale);
}

function updateDetail(ds) {

    // Get fresh stats
    var getJSONreport = function(url, successHandler, errorHandler) {
        var xhr = typeof XMLHttpRequest != 'undefined'
            ? new XMLHttpRequest()
            : new ActiveXObject('Microsoft.XMLHTTP');
        xhr.open('get', url, true);
        xhr.onreadystatechange = function() {
            var status;
            var data;
            // https://xhr.spec.whatwg.org/#dom-xmlhttprequest-readystate
            if (xhr.readyState == 4) {
                status = xhr.status;
                if (status == 200) {
                    data = JSON.parse(xhr.responseText);
                    successHandler && successHandler(data);
                }
                else {
                    errorHandler && errorHandler(status);
                }
            }
        };
        xhr.send();
    };

    // Parse JSON response
    getJSONreport('show_datastore_detail?ds='+ds, function(data) {

        // Obtener el div principal "container"
        var container = document.getElementById('container');

        // Recuperar fecha
        var fecha = data['fecha'];

        // Arreglo de muestras
        m = [];

        // committed total
        ctotal = 0;

        // Por cada elemento en la estructura JSON
        for (var i=0; i<Object.keys(data).length; i++) {
            // Recuperar vm
            var vm_name = Object.keys(data)[i];

            // Si el nombre empieza con "ds-local", ignorarlo
            if (vm_name.startsWith('fecha')) {
                continue;
            }

            // Recuperar committed en MB
            var committed = [];
            committed.push(vm_name);
            var comm = parseFloat(data[vm_name]['committed'])/1048576;
            committed.push(comm);
            m.push(committed);

            ctotal += comm;
        }

        // Arreglo de muestras condensado
        mc = [];

        // Umbral de porcentaje
        var umbral = 0.05;

        // Item para "otros"
        var otros = 0;

        // Agregar los porcentajes a cada tupla
        for (var j=0; j<m.length; j++) {
            // Si el porcentaje está por encima del umbral
            if (m[j][1]/ctotal > umbral) {
                m[j].push(m[j][1]/ctotal);
                mc.push(m[j]);
            }
            else {
                otros += m[j][1];
            }
        }

        // Agregar "otros" al arreglo condensado
        var mo = [];
        mo.push('OTRAS');
        mo.push(otros);
        mo.push(otros/ctotal);
        mc.push(mo);

        // Ahora m contiene tuplas (vm, committed, %)

        // Crear div para el gráfico
        var graph = document.createElement('div');
        graph.className = 'metrics-container';
        graph.innerHTML = '<h4>'+ds+'</h4><h5>Detalle por máquina virtual</h5>';

        // Insertar fecha
        var pdate = document.getElementById('fecha');
        // Eliminar segundos de la hora
        fecha = fecha.substr(0,fecha.lastIndexOf(':'));
        // Formatear fecha
        var afecha = fecha.split(' ');
        var adia = afecha[0].split('-');
        var dia = adia[2]+'/'+adia[1]+'/'+adia[0];
        var nfecha = dia+' '+afecha[1];
        pdate.innerHTML = '<b>Última actualización:</b> '+nfecha;
        pdate.style['display'] = 'block';

        // Crear canvas
        var canvas = document.createElement('canvas');
        canvas.setAttribute('id', ds);
        canvas.setAttribute('width', (window.innerHeight)*0.6);
        canvas.setAttribute('height', (window.innerHeight)*0.6);
        graph.appendChild(canvas);

        // Insertar gráfico
        container.appendChild(graph);

        // Dibujar tabla
        var div = document.createElement('div');
        div.className = 'metrics-table';
        var table = document.createElement('table');
        table.className = 'detail-table';
        table.setAttribute('id','detail-table-'+ds);
        table.innerHTML = '<tr><th class="left">VM</th><th class="right">Utilizado</th><th class="right">%</th></tr>';
        div.appendChild(table);
        graph.appendChild(div);

        // Dibujar gráfico de torta
        drawDetail(canvas.getContext('2d'),
            canvas.width,
            canvas.height,
            mc,
            0.9,
            table);

        // Enlace "Volver"
        var rlink = document.createElement('p');
        rlink.innerHTML = '<a href="dashboard" class="button">Volver</a>';
        container.appendChild(rlink);

    }, function(status) {
        //alert('Something went wrong.');
    });

}

function drawDetail(canvas,w,h,data,factor,table) {

    // Center coordinates
    var cx = w/2;
    var cy = h/2;

    // Radius
    var radius = cx * factor;

    // Colors
    var colors = [
        '#F03434',
        '#F1A9A0',
        '#947CB0',
        '#59ABE3',
        '#91B496',
        '#C8F7C5',
        '#95A5A6',
        '#FABE58',
        '#FDE3A7',
        '#D2D7D3',
        '#F62459',
        '#4183D7',
        '#87D37C',
        '#F89406'
    ];

    // Clear canvas
    canvas.clearRect(0,0,canvas.width,canvas.height);

    // Starting angle
    var startAngle = 0;

    for (var i=0; i<data.length; i++) {

      // Obtener siguiente porcentaje
      var value = data[i][2];

      // Calcular ángulo final
      var endAngle = startAngle+2*Math.PI*value;

      // Dibujar porción
      canvas.beginPath();
      canvas.moveTo(cx,cy);
      canvas.arc(cx, cy, radius, startAngle, endAngle, false);
      canvas.closePath();
      canvas.fillStyle = colors[i];
      canvas.fill();

      // Insertar una nueva entrada en la tabla
      var tr = document.createElement('tr');
      tr.innerHTML = '<td><span style="color: '+colors[i]+'; font-size: 85%;">\u25A0</span> '+data[i][0]+'</td>';
      tr.innerHTML += '<td class="right">'+(data[i][1]/1024).toFixed(0)+' GB</td>';
      tr.innerHTML += '<td class="right">'+(data[i][2]*100).toFixed(2)+' %</td>';
      table.appendChild(tr);

      startAngle = endAngle;

    }

    sortTable(table);
}

function showDetail(ds){
    updateDetail(ds);
}

function sortTable(table) {
// https://www.w3schools.com/howto/howto_js_sort_table.asp

  var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;

  var n = 2;

  switching = true;
  // Set the sorting direction to ascending:
  dir = "asc";
  /* Make a loop that will continue until
  no switching has been done: */
  while (switching) {
    // Start by saying: no switching is done:
    switching = false;
    rows = table.getElementsByTagName("TR");
    /* Loop through all table rows (except the
    first, which contains table headers) */
    for (i = 1; i < (rows.length - 1); i++) {
      // Start by saying there should be no switching:
      shouldSwitch = false;
      /* Get the two elements you want to compare,
      one from current row and one from the next: */
      x = rows[i].getElementsByTagName("TD")[n];
      y = rows[i + 1].getElementsByTagName("TD")[n];
      /* Check if the two rows should switch place,
      based on the direction, asc or desc: */
      if (dir == "asc") {
        if (Number(x.innerHTML) > Number(y.innerHTML)) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      } else if (dir == "desc") {
        if (Number(x.innerHTML.substr(0,x.innerHTML.lastIndexOf(' '))) < Number(y.innerHTML.substr(0,x.innerHTML.lastIndexOf(' ')))) {
          // If so, mark as a switch and break the loop:
          shouldSwitch = true;
          break;
        }
      }
    }
    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
      and mark that a switch has been done: */
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
      // Each time a switch is done, increase this count by 1:
      switchcount ++;
    } else {
      /* If no switching has been done AND the direction is "asc",
      set the direction to "desc" and run the while loop again. */
      if (switchcount == 0 && dir == "asc") {
        dir = "desc";
        switching = true;
      }
    }
  }
}
