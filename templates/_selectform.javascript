<link rel="stylesheet" href="{{ url_for('static', filename='lib/datetimepicker-master/jquery.datetimepicker.css') }}" />
<script src="{{ url_for('static', filename='lib/jquery-ui-1.14.2.custom/jquery-ui.min.js') }}"></script>
<script src="{{ url_for('static', filename='lib/datetimepicker-master/build/jquery.datetimepicker.full.min.js') }}"></script>
<script>
    
    $(document).ready(function() {
        $.datetimepicker.setLocale('en');
        $('#datetimepicker1').datetimepicker({
            format:'Y-m-d H:i',
            lang:'en'
        }
        );
    });
    $(document).ready(function() {
        $.datetimepicker.setLocale('en');
        $('#datetimepicker2').datetimepicker({
            format:'Y-m-d H:i',
            lang:'en'
        }
        );
    });
    
    
    /**
     * Prevents empty controls from being serialized into a GET query string.
     * @param {string|HTMLFormElement} formOrId  Form id or the <form> element.
     * @param {object} [opts]
     * @param {boolean} [opts.trim=true]      Treat whitespace-only as empty.
     * @param {string[]} [opts.keep=[]]       Names that should always be sent, even when empty.
     * @returns {(() => void)|null}           A cleanup fn that removes the listener.
     */
    function omitEmptyOnSubmit(formOrId, opts = {}) {
      const form = typeof formOrId === 'string' ? document.getElementById(formOrId) : formOrId;
      if (!(form instanceof HTMLFormElement)) {
        console.warn('omitEmptyOnSubmit: no <form> found for', formOrId);
        return null;
      }

      const { trim = true, keep = [] } = opts;
      const keepSet = new Set(keep);

      const isEmpty = (el) => {
        switch (el.type) {
          case 'checkbox':
          case 'radio':
            return !el.checked;
          case 'file':
            return el.files.length === 0;
          default:
            if (el.multiple) {
              return ![...el.selectedOptions].some(o => o.value !== '');
            }
            return trim ? el.value.trim() === '' : el.value === '';
        }
      };

      const onSubmit = () => {
        const disabled = [];
        for (const el of form.elements) {
          // Only touch named, submittable controls; never re-enable something already disabled
          if (!el.name || el.disabled || el.tagName === 'FIELDSET') continue;
          if (keepSet.has(el.name)) continue;
          if (isEmpty(el)) {
            el.disabled = true;
            disabled.push(el);
          }
        }
        // Restore after the request has been fired off (keeps Back/Forward usable)
        if (disabled.length) setTimeout(() => disabled.forEach(el => (el.disabled = false)), 0);
      };

      form.addEventListener('submit', onSubmit);
      return () => form.removeEventListener('submit', onSubmit);
    }
    
    // Send an empty "page" param on purpose, and don't strip whitespace-only values
    const teardown = omitEmptyOnSubmit('id_selector_form', { trim: false, keep: ['page'] });
    
    
    //provide Searcable input field to search at table, source: https://codepen.io/f_taleh/pen/jwWVqW
    $(document).ready(function(){
        $("#searchText").keyup(function(){
            _this = this;
              $.each($("#device_tracker_table_id tr"), function() {
                 if($(this).text().toLowerCase().indexOf($(_this).val().toLowerCase()) === -1){
                     $(this).hide();
                   }else{
                     $(this).show();
                  }
              });
        });
    });
    
    
    // delete all form content in container "id_selector_form" in one go: click button id="clearBtn"
    document.getElementById('clearBtn').addEventListener('click', function () {
      const container = document.getElementById('id_selector_form');

      // Reset all <input> elements
      container.querySelectorAll('input').forEach(function (input) {
        if (input.type === 'checkbox' || input.type === 'radio') {
          input.checked = false;
        } else {
          input.value = '';
        }
      });

      // Clear <textarea> and <select>
      container.querySelectorAll('textarea, select').forEach(function (el) {
        el.value = '';
      });
    });
</script>
