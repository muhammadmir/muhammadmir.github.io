function formatProp(properties) {
    str = ''
    for (var i = 0; i < properties.length; i++) {
        str += '<tr>'
        str += '<td style="background-color: #f2f2f2; text-align: center; font-weight:bold" colspan="6">Schedule Meeting Times #' + (i + 1).toString() + '</td>'
        str += '</tr>'

        str += '<tr>'
        str += '<td style="font-weight:bold">Type</td>'
        str += '<td style="font-weight:bold">Nature</td>'
        str += '<td style="font-weight:bold">Time</td>'
        str += '<td style="font-weight:bold">Days</td>'
        str += '<td style="font-weight:bold">Location</td>'
        str += '<td style="font-weight:bold">Instructors</td>'
        str += '</tr>'

        str += '<td>' + properties[i].Type.Name + '</td>'
        str += '<td>' + properties[i].Nature.Name + '</td>'
        str += '<td>' + properties[i].Time.Name + '</td>'
        str += '<td>' + properties[i].Days.map(day => day.Name).join(', ') + '</td>'
        str += '<td>' + properties[i].Location.Name + '</td>'
        str += '<td>' + properties[i].Instructors.map(instr => instr.Name).join(', ') + '</td>'
        str += '</tr>'
    }
    return str
}

function formatCRN(crn) {
    if (crn != null) return '<tr><td colspan="6"><b>CRN: </b>' + crn + '</td></tr>';
    else return '';
}

function formatDesc(description) {
    if (description != null) return '<tr><td colspan="6"><b>Description: </b>' + description + '</td></tr>';
    else return ''
}

function formatAttr(attributes) {
    if (attributes != null) return '<tr><td colspan="6"><b>Attributes: </b>' + attributes.map(attr => attr.Name).join(", ") + '</td></tr>';
    else return ''
}

/* Formatting function for row details - modify as you need */
function format(course) {
    return (
        '<table width=100%>' +
        formatCRN(course.CRN) + formatDesc(course.Description) + formatAttr(course.Attributes) + formatProp(course.Properties) +
        '</table>'
    );
}

$(document).ready(function () {
    var table = $('#courses').DataTable({
        dom: 'Pfrtip',
        paging: false,
        scrollCollapse: true,
        scrollY: 600,
        ajax: {
            url: "table.json",
            dataSrc: ""
        },
        searchPanes: {
            cascadePanes: true,
            combiner: 'and'
        },
        columnDefs: [
            {
                visible: false,
                targets: [2, 7, 13, 14, 15, 16, 17, 18, 19]
            },
            {
                searchPanes: {
                    show: false
                },
                targets: [1, 2, 4, 6, 7, 8, 10, 11, 12]
            },
            {
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
                    ]
                },
                targets: [5]
            },
            {
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
                                return rowData.Remaining <= 0
                            }
                        },
                        {
                            label: 'Waitlisted',
                            value: function (rowData, rowIdx) {
                                return rowData.Waitlisted > 0
                            }
                        }
                    ]
                },
                targets: [9]
            }
        ],
        columns: [
            {
                className: 'dt-control',
                orderable: true,
                data: null,
                defaultContent: '',
            },
            {
                data: 'Section',
            },
            {
                data: 'CRN',
            },
            {
                data: 'Subject',
                render: {
                    _: 'Name',
                },
            },
            {
                data: 'Abbreviation',
                render: {
                    _: 'Name',
                }
            },
            {
                data: 'Level',
            },
            {
                data: 'Name',
            },
            {
                data: 'Description',
            },
            {
                data: 'Credits',
            },
            {
                data: 'Capacity',
            },
            {
                data: 'Registered',
            },
            {
                data: 'Remaining',
            },
            {
                data: 'Waitlisted',
            },
            {
                data: 'Attributes',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    orthogonal: 'sp',
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Type.Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Time.Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties.0.Days',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Location.Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties',
                render: {
                    sp: '[].Nature.Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            },
            {
                data: 'Properties.0.Instructors',
                render: {
                    sp: '[].Name'
                },
                searchPanes: {
                    orthogonal: 'sp'
                }
            }
        ],
    });

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


});
