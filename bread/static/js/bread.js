/*global $, o_field, URI, window, valid_sorting_columns, document*/

function split(s, sep) {
    "use strict";
    // Split string 's' on separator 'sep' and return an array of the results.
    // Unlike Javascript's built-in split, if this one is passed an empty
    // string, it returns an empty array.
    return s === '' ? [] : s.split(sep);
}

function get_fresh_ordering_link(current_o, column_number, dir) {
    "use strict";
    /* Return a new link for the current page that changes the
    values of the column_number-th column to dir 'a' for ascending or 'd' for
    descending or '' for unsorted, and makes it the primary sorting
    field if we're sorting on it.

    current_o is the current value of the 'o' query parameter.
    */

    var parts = split(current_o, ','), part, new_parts, column_numbers, i;

    /* Get the column numbers in the current ordering parm, without
      any leading '-' and converted to Numbers.  While we're at it,
      remove any duplicate specs from 'parts', and leave out the
      column we're changing if it's in there.
     */
    column_numbers = [];
    new_parts = [];
    for (i = 0; i < parts.length; i += 1) {
        part = Math.abs(Number(parts[i]));
        if (part !== column_number && column_numbers.indexOf(part) === -1) {
            column_numbers.push(part);
            new_parts.push(parts[i]);
        }
    }
    parts = new_parts;
    /* Okay, if we're sorting on this column, then make a new parameter for this
      column and put it in front. It becomes the primary sort field.
     */
    if (dir === 'a') {
        parts = [String(column_number)].concat(parts);
    } else if (dir === 'd') {
        parts = ['-' + String(column_number)].concat(parts);
    }
    //else {
        // don't sort on this field anymore
    //}
    return URI(window.location.href).setQuery('o', parts.join(',')).href();
}

function update_th(column_number, link, marker) {
    "use strict";
    /* Find the column_number-th th element and change it to be
       a link to `link`, also inserting `marker` at the end if provided.
     */
    var new_html, $new_html, $th;
    $th = $($('th.col_header')[column_number]);
    new_html = document.createElement('a');
    $new_html = $(new_html);
    $new_html.attr('href', link);
    if (marker) {
        $new_html.html($th.html() + ' (' + marker + ")");
    } else {
        $new_html.html($th.html());
    }
    $th.html(new_html);
    $th.addClass('sortable');
}

function update_th_headers() {
    "use strict";
    /* This is run after page load. It goes through the column headers of the browse
        table and modifies them to show the current sorting and so that clicking the
        column headers changes the sorting.
     */
    var columns_done = {}, sort_parm_index, sortspec, o_parms, direction, link, marker, column_number, num_columns;
    if (o_field) {
        o_parms = split(o_field, ',');
        // Process the columns mentioned in the current ordering spec
        for (sort_parm_index = 0; sort_parm_index < o_parms.length; sort_parm_index += 1) {
            sortspec = o_parms[sort_parm_index];
            column_number = Math.abs(Number(sortspec));
            /* Skip if column is not sortable */
            if (valid_sorting_columns.indexOf(column_number) !== -1) {
                direction = sortspec.match(/^-/) ? 'd' : 'a';
                if (direction === 'a') {
                    marker = (sort_parm_index + 1) + ' ▲';
                    /* If they click on a column that's currently sorted ascending,
                       change it to descending.
                     */
                    link = get_fresh_ordering_link(o_field, column_number, 'd');
                } else {
                    marker = (sort_parm_index + 1) + ' ▼';
                    /* If they click on a column that's currently sorted descending,
                       change it to unsorted.
                     */
                    link = get_fresh_ordering_link(o_field, column_number, '');
                }
                update_th(column_number, link, marker);
            }
            columns_done[column_number] = true;
        }
    }
    // Do any columns that we haven't already done, providing a link to sort 'a'scending
    num_columns = $('th.col_header').length;
    for (column_number = 0; column_number < num_columns; column_number += 1) {
        /* Skip if it's already in the ordering param */
        if (!columns_done.hasOwnProperty(column_number)) {
            /* Skip if column is not sortable */
            if (valid_sorting_columns.indexOf(column_number) !== -1) {
                /* If they click on a column that's currently unsorted,
                   change it to sort ascending.
                 */
                link = get_fresh_ordering_link(o_field, column_number, 'a');
                update_th(column_number, link);
            }
        }
    }
}

$(function () {
    "use strict";
    update_th_headers();
});
