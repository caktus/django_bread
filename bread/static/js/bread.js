/*global $, o_field, URI, window, valid_sorting_columns, document*/

$(function () {
    "use strict";

    var SORT_ASC = 'sort_asc',
        SORT_DESC = 'sort_desc',
        UNSORTED = 'unsorted';

    function split(s, sep) {
        // Split string 's' on separator 'sep' and return an array of the results.
        // Unlike Javascript's built-in String.split, if this one is passed an empty
        // string, it returns an empty array.
        return s === '' ? [] : s.split(sep);
    }

    function get_fresh_ordering_link(current_o, column_number, dir) {
        /* Return a new link for the current page that changes the
         values of the column_number-th column to dir (SORT_ASC for ascending
         or SORT_DESC for descending or UNSORTED for unsorted), and makes it
         the primary sorting field if we're sorting on it.

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
        if (dir === SORT_ASC) {
            parts = [String(column_number)].concat(parts);
        } else if (dir === SORT_DESC) {
            parts = ['-' + String(column_number)].concat(parts);
        }
        //else {
        // don't sort on this field anymore
        //}
        return URI(window.location.href).setQuery('o', parts.join(',')).href();
    }

    function update_th(column_number, link, attrs, classes) {
        /* Find the column_number-th th element and change it to be
         a link to `link`, also adding any CSS classes (classes should
         be a string with space-separated class names), and setting
         or updating any attributes (attrs should be a dictionary).
         */
        var new_html, $new_html, $th;
        $th = $($('th.col_header')[column_number]);
        new_html = document.createElement('a');
        $new_html = $(new_html);
        $new_html.attr('href', link);
        $new_html.html($th.html());
        $th.html(new_html);
        $th.addClass(classes);
        $th.attr(attrs);
    }

    function update_th_headers() {
        /* This is run after page load. It goes through the column headers of the browse
         table and modifies them to show the current sorting and so that clicking the
         column headers changes the sorting.
         */
        var columns_done = {}, sort_parm_index, sortspec, o_parms, direction, link, column_number, num_columns, classes, next_direction, attrs;
        if ('o_field' in window && o_field) {
            o_parms = split(o_field, ',');
            // Process the columns mentioned in the current ordering spec
            for (sort_parm_index = 0; sort_parm_index < o_parms.length; sort_parm_index += 1) {
                sortspec = o_parms[sort_parm_index];
                column_number = Math.abs(Number(sortspec));
                /* Skip if column is not sortable */
                if (valid_sorting_columns.indexOf(column_number) !== -1) {
                    direction = sortspec.match(/^-/) ? SORT_DESC : SORT_ASC;
                    next_direction = direction === SORT_ASC ? SORT_DESC : UNSORTED;
                    link = get_fresh_ordering_link(o_field, column_number, next_direction);
                    attrs = {'sort_column': sort_parm_index + 1};
                    classes = 'sortable' + ' ' + direction;
                    update_th(column_number, link, attrs, classes);
                }
                columns_done[column_number] = true;
            }
        }
        // Do any columns that we haven't already done, providing a link to sort ascending
        num_columns = $('th.col_header').length;
        attrs = {};
        classes = 'sortable ' + UNSORTED;
        for (column_number = 0; column_number < num_columns; column_number += 1) {
            /* Skip if it's already in the ordering param */
            if (!columns_done.hasOwnProperty(column_number)) {
                /* Skip if column is not sortable */
                if (valid_sorting_columns.indexOf(column_number) !== -1) {
                    /* If they click on a column that's currently unsorted,
                     change it to sort ascending.
                     */
                    link = get_fresh_ordering_link(o_field, column_number, SORT_ASC);
                    update_th(column_number, link, attrs, classes);
                }
            }
        }
    }

    update_th_headers();
});
