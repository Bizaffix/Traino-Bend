from .models import DocumentQuiz, QuizQuestions
from django import forms
from django.core.exceptions import ValidationError
from dal import autocomplete
import djhacker
from .models import UserDocuments, Departments


def validate_question(value):
    print("in question validation")
    if value == '' or value is None:
        msg = 'Question field is required'
        print("Question field is required")
        raise ValidationError(msg)

def validate_option(value):
    if value == '' or value is None:
        msg = 'That option is required'
        print("That option is required")
        raise ValidationError(msg)

def validate_answer(value):
    if value != '':
        msg = 'Answer is required'
        raise ValidationError(msg)

class QuizQuestionsForm(forms.ModelForm):
    class Meta:
        model = QuizQuestions
        fields = ('id','question','option_1', 'option_2', 'option_3', 'option_4','answer', 'document',)
        # exclude = ('document', )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print("Validating question and options")
        # self.fields['question'].validators.append(validate_question)
        # self.fields['option_1'].validators.append(validate_option)
        # self.fields['option_2'].validators.append(validate_option)
        # self.fields['option_3'].validators.append(validate_option)
        # self.fields['option_4'].validators.append(validate_option)
        #self.fields['answer'].validators.append(validate_answer)

        for visible in self.visible_fields():
            if visible.field.label == 'Answer':
                visible.field.widget.attrs['class'] = 'correct-answer'
            elif visible.field.label == 'Option 1' or visible.field.label == 'Option 2' or visible.field.label == 'Option 3' or visible.field.label == 'Option 4':
                visible.field.widget.attrs['class'] = 'vRadioTextField'

    def clean(self):
        cleaned_data = super(QuizQuestionsForm, self).clean()
        question = cleaned_data.get('question')
        option_1 = cleaned_data.get('option_1')
        option_2 = cleaned_data.get('option_2')
        option_3 = cleaned_data.get('option_3')
        option_4 = cleaned_data.get('option_4')
        if question == '' or question == None:
            msg = 'Question is required'
            self.add_error('question', msg)

        if option_1 == '' or option_1 == None:
            msg = 'Answer A is required'
            self.add_error('option_1', msg)

        if option_2 == '' or option_2 == None:
            msg = 'Answer B is required'
            self.add_error('option_2', msg)

        if option_3 == '' or option_3 == None:
            msg = 'Answer C is required'
            self.add_error('option_3', msg)

        if option_4 == '' or option_4 == None:
            msg = 'Answer D is required'
            self.add_error('option_4', msg)

class AttemptQuizForm(forms.Form):
    question_ids = forms.CharField(max_length=255)

    def clean(self):
        cleaned_data = super().clean()
        question_ids = cleaned_data.get('question_ids')
        # print("test 1")
        # print(question_ids)
        if(question_ids is not None):
            question_ids = question_ids.split(',')
            for question_id in question_ids:
                answer = cleaned_data.get('question_'+question_id+"_options")
                print(answer)
                if answer == '' or answer is None:
                    raise forms.ValidationError("Please select one answer.")
                elif not answer >= 0 or answer < 4:
                    raise forms.ValidationError("Invalid answer provided.")

class DocumentForm(forms.ModelForm):
    company = djhacker.formfield(
        UserDocuments.company,
        forms.ModelChoiceField,
        widget=autocomplete.ModelSelect2(url='company_autocomplete')
    )

    department = djhacker.formfield(
        UserDocuments.department,
        forms.ModelMultipleChoiceField,
        widget=autocomplete.ModelSelect2Multiple(url='department_autocomplete', forward=['company'])
    )

    class Meta:
        model = UserDocuments
        fields = '__all__'           