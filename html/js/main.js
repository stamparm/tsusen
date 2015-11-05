var DAY_SUFFIXES = { 1: "st", 2: "nd", 3: "rd" };
var DATATABLES_COLUMNS = { PROTO: 0, DST_PORT: 1, DST_IP: 2, SRC_IP: 3, FIRST_SEEN: 4, LAST_SEEN: 5, COUNT: 6 }
var IP_COUNTRY = {};
var POINT_SIZE = 4;
var LINE_WIDTH = 1.5;
var DEFAULT_OPACITY = 0.7;
var TRENDLINE_TIMEOUT = null;
var RESIZE_TIMEOUT = null;
var REFRESH_PAGE_PERIOD = 5 * 60 * 1000;  // 5 mins

window.setTimeout(function(){ document.location.reload(true); }, REFRESH_PAGE_PERIOD);

jQuery.extend(jQuery.fn.dataTableExt.oSort, {
    // Reference: http://cdn.datatables.net/plug-ins/3cfcc339e89/sorting/date-euro.js
    "date-custom-pre": function ( a ) {
        var x = Infinity;
        var match = a.match(/time=["']([^"']+)/);
        if (match !== null) {
            var frDatea = match[1].split(' ');
            var frTimea = frDatea[1].split('.')[0].split(':');
            var frDatea2 = frDatea[0].split('-');

            x = (frDatea2[0] + frDatea2[1] + frDatea2[2] + frTimea[0] + frTimea[1] + frTimea[2]) * 1;
        }
        return x;
    },
    "date-custom-asc": function ( a, b ) {
        return a - b;
    },
    "date-custom-desc": function ( a, b ) {
        return b - a;
    }
});

jQuery.extend(jQuery.fn.dataTableExt.oSort, {
    // Reference: https://cdn.datatables.net/plug-ins/3cfcc339e89/sorting/ip-address.js
    "ip-address-pre": function (a) {
        return _ipSortingValue(a);
    },

    "ip-address-asc": function ( a, b ) {
        return ((a < b) ? -1 : ((a > b) ? 1 : 0));
    },

    "ip-address-desc": function ( a, b ) {
        return ((a < b) ? 1 : ((a > b) ? -1 : 0));
    }
});

jQuery.extend(jQuery.fn.dataTableExt.oSort, {
    "port-custom-pre": function ( a ) {
        var x = 0;
        var match = a.match(/(\d+).*/);
        if (match !== null) {
            x = match[1] * 1;
        }
        return x;
    },
    "port-custom-asc": function ( a, b ) {
        return a - b;
    },
    "port-custom-desc": function ( a, b ) {
        return b - a;
    }
});

function formatDate(value) {
    return value.getFullYear() + "-" + pad(value.getMonth() + 1, 2) + "-" + pad(value.getDate(), 2);
};

function pad(n, width, z) {
    z = z || '0';
    n = n + '';

    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

String.prototype.hashCode = function() {
    return murmurhash3_32_gc(this, 13);
};

function getHashColor(value) {
    return pad(value.hashCode().toString(16), 6).substring(0, 6);
}

// Reference: http://en.wikipedia.org/wiki/Private_network
function isLocalAddress(ip) {
    if (ip.startsWith("10.") || ip.startsWith("192.168.") || ip.startsWith("127."))
        return true;
    else if (ip.startsWith("172.")) {
        var _ = parseInt(ip.split(".")[1]);
        return ((_ >= 16) && (_ <= 31))
    }
    else
        return false;
};

function _ipSortingValue(a) {
    var x = "";

    match = a.match(/\d+\.\d+\.\d+\.\d+/);
    if (match !== null) {
        var m = match[0].split(".");

        for (var i = 0; i < m.length; i++) {
            var item = m[i];

            if(item.length === 1) {
                x += "00" + item;
            } else if(item.length === 2) {
                x += "0" + item;
            } else {
                x += item;
            }
        }
    }

    return x;
}

google.load("visualization", "1", {packages:["corechart"]});

function drawTrendlines() {
    var data = google.visualization.arrayToDataTable([
//<!TRENDLINE_DATA!>
]);

    var options = {
        title: '',
        colors: [],
        hAxis: {title: 'Date', format: 'yyyy-MM-dd', textStyle: {fontSize: 12}, titleTextStyle: {italic: false, fontSize: 13}},
        vAxis: {title: 'Intruders', textStyle: {fontSize: 12}, titleTextStyle: {italic: false, fontSize: 13}, logScale: true, minValue: 0},
        trendlines: { },
        legend: {position: 'right', textStyle: {fontSize: 13}},
        fontName: 'monospace',
        chartArea: {left: 70, top: 20, width: "80%", height: "80%"},
    };

    for (var i = 1; i < data.getNumberOfColumns(); i++) {
        var color = getHashColor(data.getColumnLabel(i));
        options.trendlines[i - 1] = {type: 'polynomial', degree: 3, opacity: 1, lineWidth: 1, tooltip: false, color: color};
        options.colors.push(color);
    }

    if (data.getNumberOfRows() > 0) {
        document.title = "tsusen (" + formatDate(data.getValue(0, 0)) + " - " + formatDate(data.getValue(data.getNumberOfRows() - 1,0)) + ")";
    }


    var chart = new google.visualization.ScatterChart(document.getElementById('chart'));

    chart.draw(data, options);

    // Reference: http://stackoverflow.com/a/20384135
    $(window).resize(function() {
        if(RESIZE_TIMEOUT)
            clearTimeout(RESIZE_TIMEOUT);
        RESIZE_TIMEOUT = setTimeout(function() {
            $(this).trigger('resized');
        }, 300);
    });

    $(window).on('resized', function() {
        drawTrendlines(chart.draw(data, options));
    });

    google.visualization.events.addListener(chart, 'onmouseover', function(e){
        var circles = $('svg g g g circle');
        if (circles.length) {
            var fill = circles[circles.length - 1].attributes["fill"].value;
            clearTimeout(TRENDLINE_TIMEOUT);
            $("circle[fill='" + fill + "']").attr("r", POINT_SIZE * 1.2).attr("fill-opacity", 1);
            $("path[stroke='" + fill + "']").attr("stroke-width", LINE_WIDTH * 2).attr("stroke-opacity", 1);
            $("circle[fill!='" + fill + "']").attr("fill-opacity", 0.1);
            $("path[stroke!='" + fill + "']").attr("stroke-opacity", 0.1);
        }
    });

    google.visualization.events.addListener(chart, 'onmouseout', function(e){
        TRENDLINE_TIMEOUT = setTimeout(function(){
            $("circle").attr("r", POINT_SIZE).attr("fill-opacity", DEFAULT_OPACITY);
            $("path").attr("stroke-width", LINE_WIDTH).attr("stroke-opacity", DEFAULT_OPACITY);
        }, 500);
    });

    google.visualization.events.addListener(chart, 'ready', function(e){
        google.visualization.events.trigger(chart, 'onmouseout', e);
    });
}


var dataset = [
//<!DATASET!>
];
 
$(document).ready(function() {
    drawTrendlines();

    $('#details').DataTable( {
        data: dataset,
        columns: [
            { title: "proto" },
            { title: "dst_port", type: "port-custom" },
            { title: "dst_ip", type: "ip-address" },
            { title: "src_ip", type: "ip-address" },
            { title: "first_seen", type: "date-custom" },
            { title: "last_seen", type: "date-custom" },
            { title: "count" },                        
        ],
        columnDefs: [
            {
                orderSequence: [ "desc", "asc" ], 
                targets: [ DATATABLES_COLUMNS.FIRST_SEEN, DATATABLES_COLUMNS.LAST_SEEN, DATATABLES_COLUMNS.COUNT ]
            },
            {
                render: function (data, type, row) {
                    var parts = data.split(' ');
                    var day = parts[0].split('-')[2];
                    var dayint = parseInt(day);
                    var suffix = (dayint > 10 && dayint < 20) ? "th" : DAY_SUFFIXES[dayint % 10] || "th";
                    return "<div time='" + data + "'><span class='time-day'>" + day + "<sup>" + suffix + "</sup></span> " + parts[1].split('.')[0] + "</div>";
                },
                targets: [ DATATABLES_COLUMNS.FIRST_SEEN, DATATABLES_COLUMNS.LAST_SEEN ],
            },
        ],
        iDisplayLength: 25,
        aaSorting: [ [DATATABLES_COLUMNS.LAST_SEEN, 'desc'] ],
        fnRowCallback: function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            function nslookup(event, ui) {
                var elem = $(this);
                var html = elem.parent().html();
                var match = html.match(/\d+\.\d+\.\d+\.\d+/);

                if (match !== null) {
                    var ip = match[0];

                    $.ajax("https://stat.ripe.net/data/dns-chain/data.json?resource=" + ip, { dataType:"jsonp", ip: ip})
                    .success(function(json) {
                        var _ = json.data.reverse_nodes[this.ip];
                        if ((_.length === 0)||(_ === "localhost")) {
                            _ = "-";
                        }
                        _ = String(_);
                        if (_.length > 40) {
                            _ = _.substring(0, 40) + "<br>" + _.substring(40);
                        }
                        var msg = "<p><b>" + _ + "</b></p>";
                        ui.tooltip.find(".ui-tooltip-content").html(msg + "please wait...");

                        $.ajax("https://stat.ripe.net/data/whois/data.json?resource=" + ip, { dataType:"jsonp", ip: ip, msg: msg })
                        .success(function(json) {
                            // Reference: http://bugs.jqueryui.com/ticket/8740#comment:21
                            var found = null;
                            var msg = "";

                            for (var i = json.data.records.length - 1; i >= 0 ; i--) {
                                if ((json.data.records[i][0].key.toLowerCase().indexOf("inetnum") != -1) || (json.data.records[i][0].key.toLowerCase().indexOf("netrange") != -1)){
                                    found = i;
                                    break;
                                }
                            }

                            if (found !== null) {
                                for (var j = 0; j < json.data.records[found].length; j++) {
                                    msg += json.data.records[found][j].key + ": " + json.data.records[found][j].value;
                                    msg += "<br>";
                                }
                                msg = msg.replace(/(\-\+)+/g, "--").replace(/(\-\+)+/g, "--");
                            }

                            ui.tooltip.find(".ui-tooltip-content").html(this.msg + msg);
                        });
                    });
                }
            }

            $('[title]', nRow).tooltip();

            $.each([DATATABLES_COLUMNS.SRC_IP, DATATABLES_COLUMNS.DST_IP], function(index, value) {
                var cell = $('td:eq(' + value + ')', nRow);

                if (cell === null)
                    return false;

                var html = cell.html();

                if (html === null)
                    return false;

                if ((html.indexOf('flag') > -1) || (html.indexOf('lan') > -1) || (html.indexOf(',') > -1))
                    return false;

                var match = html.match(/\d+\.\d+\.\d+\.\d+/);
                if (match === null)
                    return false;

                var interval = null;
                var img = "";
                var ip = match[0];
                var options = { content: "please wait...", open: nslookup, position: { my: "left center", at: "right+10 top-50" } };

                if (!isLocalAddress(ip)) {
                    if (!(ip in IP_COUNTRY)) {
                        IP_COUNTRY[ip] = null;
                        //$.ajax("https://stat.ripe.net/data/geoloc/data.json?resource=" + ip, { dataType:"jsonp", ip: ip, cell: cell })
                        $.ajax("/geoip.json?ip=" + ip, { dataType:"jsonp", ip: ip, cell: cell })
                        .success(function(json) {
                            var span_ip = $("<span title=''/>").html(this.ip + " ");

                            if ((json.country) && (json.country !== "ANO")) {
                                IP_COUNTRY[this.ip] = json.country.toLowerCase().split('-')[0];
                                img = '<img src="images/blank.gif" class="flag flag-' + IP_COUNTRY[this.ip] + '" title="' + IP_COUNTRY[this.ip].toUpperCase() + '" />';  // title="' + IP_COUNTRY[this.ip].toUpperCase() + '" 
                                span_ip.tooltip(options);
                            }
                            else {
                                IP_COUNTRY[this.ip] = "unknown";
                                img = '<img src="images/blank.gif" class="flag flag-unknown" title="UNKNOWN"/>';
                            }

                            this.cell.html("").append(span_ip).append($(img).tooltip());
                        });
                    }
                    else if (IP_COUNTRY[ip] !== null) {
                        img = ' <img src="images/blank.gif" class="flag flag-' + IP_COUNTRY[ip] + '" title="' + IP_COUNTRY[ip].toUpperCase() + '" />'

                        var span_ip = $("<span title=''/>").html(ip + " ");
                        span_ip.tooltip(options);

                        cell.html("").append(span_ip).append($(img).tooltip());
                    }
                    else {
                        interval = setInterval(function(ip, cell){
                            html = cell.html();
                            if ((IP_COUNTRY[ip] !== null) && (html.indexOf("flag-") === -1)) {
                                img = ' <img src="images/blank.gif" class="flag flag-' + IP_COUNTRY[ip] + '" title="' + IP_COUNTRY[ip].toUpperCase() + '" />'

                                var span_ip = $("<span title=''/>").html(ip + " ");
                                span_ip.tooltip(options);

                                cell.html("").append(span_ip).append($(img).tooltip());
                                clearInterval(interval);
                            }
                        }, 200, ip, cell);
                    }
                }
                else {
                    img = '<img src="images/lan.gif" height="11px" style="margin-bottom: 0px" title="LAN">';
                    cell.html(html + " ").append($(img).tooltip());
                }
            });
        },

    } );
} );
