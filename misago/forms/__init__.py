from django import forms
from django.utils.translation import ugettext_lazy as _
from misago.forms.layouts import *
from recaptcha.client.captcha import submit as recaptcha_submit

class Form(forms.Form):
    """
    Custom form implementation extending Django Forms functionality
    """
    validate_repeats = []
    repeats_errors = []
    dont_strip = []
    allow_nl = []
    error_source = None
    def __init__(self, data=None, file=None, request=None, *args, **kwargs):
        self.request = request

        # Extract request from first argument
        if data != None:
            super(Form, self).__init__(data, file, *args, **kwargs)
        else:
            super(Form, self).__init__(*args, **kwargs)

        # Kill captcha fields
        try:
            if self.request.settings['bots_registration'] != 'recaptcha' or self.request.session.get('captcha_passed'):
                del self.fields['recaptcha']
        except KeyError:
            pass
        try:
            if self.request.settings['bots_registration'] != 'qa' or self.request.session.get('captcha_passed'):
                del self.fields['captcha_qa']
            else:
                # Make sure we have any questions loaded
                self.fields['captcha_qa'].label = self.request.settings['qa_test']
                self.fields['captcha_qa'].help_text = self.request.settings['qa_test_help']
        except KeyError:
            pass

        # Let forms do mumbo-jumbo with fields removing
        self.finalize_form()

    def finalize_form(self):
        pass

    def full_clean(self):
        """
        Trim inputs and strip newlines
        """
        self.data = self.data.copy()
        for key, field in self.fields.iteritems():
            try:
                if field.__class__.__name__ in ['ModelChoiceField', 'TreeForeignKey'] and self.data[key]:
                    self.data[key] = int(self.data[key])
                elif field.__class__.__name__ == 'ModelMultipleChoiceField':
                    self.data.setlist(key, [int(x) for x in self.data.getlist(key, [])])
                elif field.__class__.__name__ not in ['DateField', 'DateTimeField']:
                    if not key in self.dont_strip:
                        if field.__class__.__name__ in ['MultipleChoiceField', 'TypedMultipleChoiceField']:
                            self.data.setlist(key, [x.strip() for x in self.data.getlist(key, [])])
                        else:
                            self.data[key] = self.data[key].strip()
                    if not key in self.allow_nl:
                        if field.__class__.__name__ in ['MultipleChoiceField', 'TypedMultipleChoiceField']:
                            self.data.setlist(key, [x.replace("\n", '') for x in self.data.getlist(key, [])])
                        else:
                            self.data[key] = self.data[key].replace("\n", '')
            except (KeyError, AttributeError):
                pass
        super(Form, self).full_clean()

    def clean(self):
        """
        Clean data, do magic checks and stuff
        """
        cleaned_data = super(Form, self).clean()
        self._check_all()
        return cleaned_data

    def clean_recaptcha(self):
        """
        Test reCaptcha, scream if it went wrong
        """
        response = recaptcha_submit(
                                    self.request.POST.get('recaptcha_challenge_field'),
                                    self.request.POST.get('recaptcha_response_field'),
                                    self.request.settings['recaptcha_private'],
                                    self.request.session.get_ip(self.request)
                                    ).is_valid
        if not response:
            raise forms.ValidationError(_("Entered words are incorrect. Please try again."))
        self.request.session['captcha_passed'] = True
        return ''

    def clean_captcha_qa(self):
        """
        Test QA Captcha, scream if it went wrong
        """

        if not unicode(self.cleaned_data['captcha_qa']).lower() in (name.lower() for name in unicode(self.request.settings['qa_test_answers']).splitlines()):
            raise forms.ValidationError(_("The answer you entered is incorrect."))
        self.request.session['captcha_passed'] = True
        return self.cleaned_data['captcha_qa']

    def _check_all(self):
        # Check repeated fields
        self._check_repeats()
        # Check CSRF, we dont allow un-csrf'd forms in Misago
        self._check_csrf()
        # Check if we have any errors from fields, if we do, we will set fancy form-wide error message
        self._check_fields_errors()

    def _check_repeats(self):
        for index, repeat in enumerate(self.validate_repeats):
            # Check empty fields
            for field in repeat:
                if not self.data[field]:
                    try:
                        if len(repeat) == 2:
                            self.errors['_'.join(repeat)] = [self.repeats_errors[index]['fill_both']]
                        else:
                            self.errors['_'.join(repeat)] = [self.repeats_errors[index]['fill_all']]
                    except (IndexError, KeyError):
                        if len(repeat) == 2:
                            self.errors['_'.join(repeat)] = [_("You have to fill in both fields.")]
                        else:
                            self.errors['_'.join(repeat)] = [_("You have to fill in all fields.")]
                    break

            else:
                # Check different fields
                past_field = self.data[repeat[0]]
                for field in repeat:
                    if self.data[field] != past_field:
                        try:
                            self.errors['_'.join(repeat)] = [self.repeats_errors[index]['different']]
                        except (IndexError, KeyError):
                            self.errors['_'.join(repeat)] = [_("Entered values differ from each other.")]
                        break
                    past_field = self.data[field]


    def _check_csrf(self):
        if not self.request.csrf.request_secure(self.request):
            raise forms.ValidationError(_("Request authorization is invalid. Please resubmit your form."))

    def _check_fields_errors(self):
        if self.errors:
            if self.error_source and self.error_source in self.errors:
                field_error, self.errors[self.error_source] = self.errors[self.error_source][0], []
                raise forms.ValidationError(field_error)
            raise forms.ValidationError(_("Form contains errors."))


class YesNoSwitch(forms.CheckboxInput):
    """
    Custom Yes-No switch as fancier alternative to checkboxes
    """
    pass
