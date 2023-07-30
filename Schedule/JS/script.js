function formatProp(properties) {
    str = ''
    for (var i = 0; i < properties.length; i++) {
        str += '<table class="format-properties-table">'

        str += '<thead class="meeting-time">'
        str += '<tr>'
        str += '<td colspan=7 style="text-align: center;">Schedule Meeting Times #' + (i + 1).toString() + '</td>'
        str += '</tr>'
        str += '</thead>'

        str += '<thead class="meeting-properties-head">'
        str += '<tr>'
        str += '<td style="font-weight:bold">Type</td>'
        str += '<td style="font-weight:bold">Nature</td>'
        str += '<td style="font-weight:bold">Time</td>'
        str += '<td style="font-weight:bold">Days</td>'
        str += '<td style="font-weight:bold">Location</td>'
        str += '<td style="font-weight:bold">Period</td>'
        str += '<td style="font-weight:bold">Instructors</td>'
        str += '</tr>'
        str += '</thead>'


        str += '<tbody class="meeting-properties-body">'
        str += '<td>' + properties[i].Type.Name + '</td>'
        str += '<td>' + properties[i].Nature.Name + '</td>'
        str += '<td>' + properties[i].Time.Name + '</td>'
        str += '<td>' + properties[i].Days.map(day => day.Name).join(', ') + '</td>'
        str += '<td>' + properties[i].Location.Name + '</td>'
        str += '<td>' + properties[i].Period.Name + '</td>'
        str += '<td>' + properties[i].Instructors.map(instr => instr.Name).join(', ') + '</td>'
        str += '</tr>'
        str += '</tbody>'

        str += '</table>'
    }
    return str
}

function formatCRN(crn) {
    if (crn != null) return '<tr><td colspan="7"><b>CRN: </b>' + crn + '</td></tr>';
    else return '';
}

function formatDesc(description) {
    if (description != null) return '<tr><td colspan="7"><b>Description: </b>' + description + '</td></tr>';
    else return ''
}

function formatAttr(attributes) {
    if (attributes != null) return '<tr><td colspan="7"><b>Attributes: </b>' + attributes.map(attr => attr.Name).join(", ") + '</td></tr>';
    else return ''
}

function formatPreReq(prerequisites) {
    if (prerequisites != null) return '<tr><td colspan="7"><b>Prerequisites: </b>' + prerequisites.join(", ") + '</td></tr>';
    else return ''
}

function formatCoReq(corequisites) {
    if (corequisites != null) return '<tr><td colspan="7"><b>Corequisites: </b>' + corequisites.join(", ") + '</td></tr>';
    else return ''
}

function formatMutualExclusions(mutualExclusions) {
    if (mutualExclusions != null) return '<tr><td colspan="7"><b>Mutual Exclusions: </b>' + mutualExclusions.join(", ") + '</td></tr>';
    else return ''
}

function formatCrossList(crossListCourses) {
    if (crossListCourses != null) return '<tr><td colspan="7"><b>Cross List Courses: </b>' + crossListCourses.join(", ") + '</td></tr>';
    else return ''
}

function formatRestrictions(restrictions) {
    if (restrictions != null) {

        let entry = '';

        restrictions.forEach(item => {
            const description = `<br><b>${item.Description}</b>`;

            let reqList = '';
            item.Requirements.forEach(requirement => {
                reqList += `<li>${requirement}</li>`;
            });

            entry += `${description}<ul>${reqList}</ul>`;
        });

        return '<tr><td colspan="7"><b>Restrictions: </b>' + entry + '</td></tr>';
    }
    else return ''
}

/* Formatting function for row details - modify as you need */
function format(course) {
    return (
        '<table class="format-table">' +
        formatCRN(course.CRN) +
        formatDesc(course.Description) +
        formatPreReq(course.Prerequisites) +
        formatCoReq(course.Corequisites) +
        formatMutualExclusions(course["Mutual Exclusions"]) +
        formatCrossList(course["Cross List Courses"]) +
        formatRestrictions(course["Restrictions"]) +
        formatAttr(course.Attributes) +
        formatProp(course.Properties) +
        '</table>'
    );
}

// https://stackoverflow.com/a/65939108
const saveFileAsJson = (filename, dataObjToWrite) => {
    const blob = new Blob([JSON.stringify(dataObjToWrite)], { type: "text/json" });
    const link = document.createElement("a");

    link.download = filename;
    link.href = window.URL.createObjectURL(blob);
    link.dataset.downloadurl = ["text/json", link.download, link.href].join(":");

    const evt = new MouseEvent("click", {
        view: window,
        bubbles: true,
        cancelable: true,
    });

    link.dispatchEvent(evt);
    link.remove()
};

function createTable() {
    return $('#courses').DataTable({
        data: JSON.parse(sessionStorage['Courses'])[0]['Courses'],
        dom: 'Pfrtip',
        searchPanes: {
            cascadePanes: true,
            threshold: 1.0,
        },
        columnDefs: [
            {
                visible: false,
                targets: [1, 7, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]
            },
            {
                searchPanes: {
                    show: false
                },
                targets: [1, 2, 4, 6, 6, 7, 8, 10, 11, 12]
            },
            {
                searchPanes: {
                    show: true,
                    combiner: sessionStorage['Pane Logic'].toLowerCase()
                },
                targets: [3, 18, 19, 20, 21, 22, 23, 24]
            },
            { // Filter by course level
                searchPanes: {
                    options: [
                        {
                            label: "000-199",
                            value: function (rowData, rowIdx) {
                                let courseLevel = parseInt(rowData.Level)
                                return courseLevel <= 199
                            }
                        },
                        {
                            label: "200-299",
                            value: function (rowData, rowIdx) {
                                let courseLevel = parseInt(rowData.Level)
                                return courseLevel >= 200 && courseLevel <= 299
                            }
                        },
                        {
                            label: "300-499",
                            value: function (rowData, rowIdx) {
                                let courseLevel = parseInt(rowData.Level)
                                return courseLevel >= 300 && courseLevel <= 499
                            }
                        },
                        {
                            label: "500-999",
                            value: function (rowData, rowIdx) {
                                let courseLevel = parseInt(rowData.Level)
                                return courseLevel >= 500 && courseLevel <= 999
                            }
                        }
                    ],
                    combiner: sessionStorage['Pane Logic'].toLowerCase()
                },
                targets: [5]
            },
            { // Filter by capacity: Available, Full, Waitlisted
                searchPanes: {
                    options: [
                        {
                            label: 'Available',
                            value: function (rowData, rowIdx) {
                                return rowData.Remaining > 0
                            }
                        },
                        {
                            label: 'Full',
                            value: function (rowData, rowIdx) {
                                return rowData.Remaining <= 0 && rowData.Waitlisted <= 0
                            }
                        },
                        {
                            label: 'Waitlisted',
                            value: function (rowData, rowIdx) {
                                return rowData.Waitlisted > 0
                            }
                        }
                    ],
                    combiner: sessionStorage['Pane Logic'].toLowerCase()
                },
                targets: [9]
            }
        ],
        columns: [
            { // 0
                className: 'dt-control',
                orderable: true,
                data: null,
                defaultContent: '',
            },
            {
                data: 'CRN',
            },
            { // 2
                data: 'Section',
            },
            {
                data: 'Subject',
                render: {
                    _: 'Name',
                },
            },
            { // 4
                data: 'Abbreviation',
                render: {
                    _: 'Name',
                }
            },
            {
                data: 'Level',
            },
            { // 6
                data: 'Name',
            },
            {
                data: 'Description',
            },
            { // 8
                data: 'Credits',
            },
            {
                data: 'Capacity',
            },
            { // 10
                data: 'Registered',
            },
            {
                data: 'Remaining',
            },
            { // 12
                data: 'Waitlisted',
            },
            {
                data: 'Prerequisites',
            },
            { // 14
                data: 'Corequisites',
            },
            {
                data: 'Mutual Exclusions',
            },
            { // 16
                data: 'Cross List Courses',
            },
            {
                data: 'Restrictions',
            },
            { // 18
                data: 'Attributes',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    header: 'Attribute',
                    orthogonal: 'sp',
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Type.Name'
                },
                searchPanes: {
                    header: 'Type',
                    orthogonal: 'sp'
                }
            },
            { // 20
                data: 'Properties',
                render: {
                    sp: '[].Time.Name'
                },
                searchPanes: {
                    header: 'Time',
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties.0.Days',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    header: 'Day',
                    orthogonal: 'sp'
                }
            },
            { // 22
                data: 'Properties',
                render: {
                    sp: '[].Location.Name'
                },
                searchPanes: {
                    header: 'Location',
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Nature.Name'
                },
                searchPanes: {
                    header: 'Nature',
                    orthogonal: 'sp'
                }
            },
            { // 24
                data: 'Properties.0.Instructors',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    header: 'Instructor',
                    orthogonal: 'sp'
                }
            }
        ],
    });
}

function detectDevice() {
    const platform = navigator.platform.toLowerCase();
    const isMac = platform.includes('mac');
    const isWindows = platform.includes('win');

    if (isMac) return "Mac"
    if (isWindows) return "Windows"
    return "Neither"
}

sessionStorage['Pane Logic'] = sessionStorage['Pane Logic'] == undefined ? 'OR' : sessionStorage['Pane Logic'];

$(document).ready(function () {
    document.getElementById('paneLogic').textContent = 'Logic: ' + sessionStorage['Pane Logic'];
    let table = createTable();
    
    // Add event listener for opening and closing details
    $('#courses tbody').on('click', 'td.dt-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child(format(row.data())).show();
            tr.addClass('shown');
        }
    });

    document.getElementById('calendarName').textContent = 'Calendar: ' + JSON.parse(sessionStorage['Courses'])[0]['Calendar Name'];

    let device = detectDevice();
    let keyboardTipPrefix = 'Tip: To select multiple Options in one or more Search Panes, press ';

    keyboardTipPrefix += device == 'Mac' ? '<kbd>⌘</kbd> + Click' :  '<kbd>Ctrl</kbd> + Click';
    keyboardTipPrefix = device == 'Neither' ? 'Tip: View this page on a computer!' : keyboardTipPrefix;

    document.getElementById('keyboardTip').innerHTML = keyboardTipPrefix

    document.getElementById('paneLogic').addEventListener('click', () => {
        sessionStorage['Pane Logic'] = sessionStorage['Pane Logic'] == 'OR' ? 'AND' : 'OR';
        console.log(sessionStorage['Pane Logic']);

        document.getElementById('paneLogic').textContent = 'Inter-Pane Logic: ' + sessionStorage['Pane Logic'];
        location.reload();
    });

    document.getElementById('downloadSelectedRows').addEventListener('click', () => {
        let data = Array.from(table.rows({search: 'applied'}).data());
        saveFileAsJson('Filtered.json', data);
    });
});

