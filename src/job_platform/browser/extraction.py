"""In-page form extraction script (docs/06 Structured Form Extraction).

One deterministic `page.evaluate` call returns everything the engine needs:
form fields with resolved labels and selectors, candidate actions, and the
raw signals the safety detectors consume. No candidate data is involved —
only page structure.
"""

EXTRACTION_SCRIPT = r"""
() => {
  const isVisible = (el) => {
    if (el.type === 'hidden') return false;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 &&
           style.display !== 'none' && style.visibility !== 'hidden';
  };

  const cssEscape = (value) => CSS.escape(value);

  const labelFor = (el) => {
    if (el.getAttribute('aria-label')) return el.getAttribute('aria-label').trim();
    const labelledBy = el.getAttribute('aria-labelledby');
    if (labelledBy) {
      const parts = labelledBy.split(/\s+/)
        .map((id) => document.getElementById(id))
        .filter(Boolean)
        .map((node) => node.innerText.trim());
      if (parts.length) return parts.join(' ');
    }
    if (el.id) {
      const label = document.querySelector(`label[for="${cssEscape(el.id)}"]`);
      if (label) return label.innerText.trim();
    }
    const wrapping = el.closest('label');
    if (wrapping) return wrapping.innerText.trim();
    return el.getAttribute('placeholder') || '';
  };

  const sectionFor = (el) => {
    const fieldset = el.closest('fieldset');
    if (fieldset) {
      const legend = fieldset.querySelector('legend');
      if (legend) return legend.innerText.trim();
    }
    const section = el.closest('section');
    if (section) {
      const heading = section.querySelector('h1,h2,h3');
      if (heading) return heading.innerText.trim();
    }
    return '';
  };

  const selectorFor = (el) => {
    if (el.id) return `#${cssEscape(el.id)}`;
    if (el.name) return `[name="${cssEscape(el.name)}"]`;
    return '';
  };

  const formIdFor = (el) => {
    const form = el.closest('form');
    if (!form) return '';
    const index = Array.prototype.indexOf.call(document.forms, form);
    return form.id || form.getAttribute('name') || `form_${index}`;
  };

  const fields = [];
  const radioGroups = {};

  document.querySelectorAll('input, select, textarea').forEach((el) => {
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    if (type === 'submit' || type === 'button' || type === 'image') return;
    const visible = isVisible(el);

    if (tag === 'input' && type === 'radio') {
      const name = el.name || '(unnamed)';
      if (!radioGroups[name]) {
        radioGroups[name] = {
          field_id: name,
          label: sectionFor(el) || name,
          field_type: 'radio',
          input_type: 'radio',
          required: el.required,
          current_value: '',
          options: [],
          selector: `[name="${cssEscape(el.name)}"]`,
          section: sectionFor(el),
          visible: visible,
          enabled: !el.disabled,
          read_only: false,
          placeholder: '',
          help_text: '',
          autocomplete: '',
          form_id: formIdFor(el),
        };
        fields.push(radioGroups[name]);
      }
      const group = radioGroups[name];
      group.options.push(el.value || labelFor(el));
      group.visible = group.visible || visible;
      if (el.checked) group.current_value = el.value;
      return;
    }

    let fieldType = 'unknown';
    let options = [];
    let currentValue = '';
    if (tag === 'select') {
      fieldType = 'select';
      options = Array.from(el.options).map((o) => o.label.trim() || o.value);
      const selected = el.options[el.selectedIndex];
      currentValue = selected ? (selected.label.trim() || selected.value) : '';
    } else if (tag === 'textarea') {
      fieldType = 'textarea';
      currentValue = el.value;
    } else if (type === 'checkbox') {
      fieldType = 'checkbox';
      currentValue = el.checked ? 'true' : 'false';
    } else if (type === 'file') {
      fieldType = 'file';
      currentValue = el.files && el.files.length ? el.files[0].name : '';
    } else {
      const map = { email: 'email', tel: 'phone', number: 'number', url: 'url',
                    password: 'password', date: 'date', hidden: 'hidden' };
      fieldType = map[type] || 'text';
      currentValue = el.value;
    }

    fields.push({
      field_id: el.id || el.name || `${tag}_${fields.length}`,
      label: labelFor(el),
      field_type: fieldType,
      input_type: type || tag,
      required: el.required || el.getAttribute('aria-required') === 'true',
      current_value: currentValue,
      options: options,
      placeholder: el.getAttribute('placeholder') || '',
      help_text: '',
      section: sectionFor(el),
      selector: selectorFor(el),
      visible: visible,
      enabled: !el.disabled,
      read_only: el.readOnly === true,
      autocomplete: (el.getAttribute('autocomplete') || '').toLowerCase(),
      form_id: formIdFor(el),
    });
  });

  const actions = [];
  document.querySelectorAll(
    'button, input[type="submit"], input[type="button"], a[role="button"]'
  ).forEach((el, index) => {
    if (!isVisible(el)) return;
    const text = (el.innerText || el.value || '').trim();
    const lowered = text.toLowerCase();
    let type = 'unknown';
    if (/submit|apply now|finish|send application/.test(lowered)) type = 'submit';
    else if (/next|continue|save and continue|proceed/.test(lowered)) type = 'next';
    else if (/back|previous/.test(lowered)) type = 'back';
    actions.push({
      action_id: el.id || `action_${index}`,
      type: type,
      label: text,
      selector: el.id ? `#${cssEscape(el.id)}` : '',
      form_id: formIdFor(el),
    });
  });

  const errorNodes = document.querySelectorAll(
    '[role="alert"], .field-error, .error-message, [aria-invalid="true"]'
  );
  const validationErrors = Array.from(errorNodes)
    .filter((el) => isVisible(el) && el.innerText && el.innerText.trim())
    .map((el) => el.innerText.trim());

  return {
    title: document.title,
    heading: (document.querySelector('h1') || {}).innerText || '',
    fields: fields,
    actions: actions,
    validation_errors: validationErrors,
    content: {
      text: document.body ? document.body.innerText.slice(0, 8000) : '',
      html_classes: Array.from(document.querySelectorAll('[class]'))
        .slice(0, 300)
        .map((el) => el.className && el.className.toString ? el.className.toString() : '')
        .join(' '),
      iframe_titles: Array.from(document.querySelectorAll('iframe'))
        .map((f) => (f.title || '') + ' ' + (f.src || '')),
      has_password_field: !!document.querySelector('input[type="password"]'),
      has_one_time_code_field: !!document.querySelector(
        'input[autocomplete="one-time-code"]'
      ),
    },
  };
}
"""
